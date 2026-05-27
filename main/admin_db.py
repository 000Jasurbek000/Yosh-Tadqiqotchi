"""
Admin panel uchun baza boshqaruvi:
 - Bazani yuklab olish (download) — foydalanuvchilar SAQLANADI (export qilinmaydi)
 - Bazani yuklash (upload)   — foydalanuvchilarga TEGMAYDI
 - Bazani tozalash (clear)    — admin foydalanuvchilarni ham o'chirishni tanlaydi
"""
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db import connection


# ===== Yordamchi funksiyalar =====

def _db_path():
    return str(settings.DATABASES['default']['NAME'])


def _backups_dir():
    path = os.path.join(settings.BASE_DIR, 'db_backups')
    os.makedirs(path, exist_ok=True)
    return path


def _user_tables():
    """Foydalanuvchilarga tegishli jadvallar ro'yxati."""
    tables = {
        'auth_user',
        'auth_user_groups',
        'auth_user_user_permissions',
    }
    try:
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        utable = UserModel._meta.db_table
        tables.add(utable)
        tables.add(f'{utable}_groups')
        tables.add(f'{utable}_user_permissions')
    except Exception:
        pass
    return tables


def _system_tables():
    """Django tizim jadvallari (migratsiya, content types, va h.k.) — hech qachon tegmaymiz."""
    return {
        'django_migrations',
        'django_content_type',
        'django_session',
        'django_admin_log',
        'auth_permission',
        'auth_group',
        'auth_group_permissions',
    }


# ===== Download =====

@staff_member_required
def download_db(request):
    """Joriy SQLite bazani yuklab beradi, lekin foydalanuvchi ma'lumotlari OLIB TASHLANADI."""
    db_path = _db_path()
    if not os.path.exists(db_path):
        messages.error(request, "Baza fayli topilmadi.")
        return HttpResponseRedirect(reverse('admin:index'))

    # Vaqtinchalik nusxa yaratamiz, undan foydalanuvchi jadvallarini tozalaymiz
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.sqlite3', prefix='dbexport_')
    os.close(tmp_fd)

    try:
        shutil.copy2(db_path, tmp_path)

        con = sqlite3.connect(tmp_path)
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = OFF;")
        for tbl in _user_tables():
            try:
                cur.execute(f'DELETE FROM "{tbl}";')
            except sqlite3.OperationalError:
                pass
        con.commit()
        try:
            cur.execute("VACUUM;")
        except Exception:
            pass
        con.close()

        with open(tmp_path, 'rb') as f:
            data = f.read()
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"db_backup_{timestamp}.sqlite3"

    response = HttpResponse(data, content_type='application/x-sqlite3')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ===== Upload =====

@staff_member_required
@require_http_methods(["GET", "POST"])
def upload_db(request):
    """Yuklangan SQLite fayldan ma'lumotlarni joriy bazaga import qiladi.
    Foydalanuvchi jadvallariga TEGMAYDI."""
    if request.method == "POST":
        uploaded = request.FILES.get('database_file')
        confirm = request.POST.get('confirm') == 'yes'

        if not uploaded:
            messages.error(request, "Fayl tanlanmagan.")
            return HttpResponseRedirect(reverse('admin:db_upload'))
        if not confirm:
            messages.error(request, "Tasdiqlash katakchasini belgilang.")
            return HttpResponseRedirect(reverse('admin:db_upload'))

        first_bytes = uploaded.read(16)
        uploaded.seek(0)
        if not first_bytes.startswith(b'SQLite format 3'):
            messages.error(request, "Yuklangan fayl SQLite formatida emas. Faqat .sqlite3 fayl yuklang.")
            return HttpResponseRedirect(reverse('admin:db_upload'))

        db_path = _db_path()
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1) Yuklangan faylni vaqtincha saqlash
        tmp_fd, tmp_upload = tempfile.mkstemp(suffix='.sqlite3', prefix='dbupload_')
        os.close(tmp_fd)
        try:
            with open(tmp_upload, 'wb') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            # 2) Joriy bazadan zaxira nusxa
            if os.path.exists(db_path):
                backup_path = os.path.join(_backups_dir(), f'db_before_upload_{ts}.sqlite3')
                shutil.copy2(db_path, backup_path)

            # 3) Django ulanishini yopamiz
            connection.close()

            # 4) Joriy bazaga ulanib, yuklanganini ATTACH qilamiz
            user_tables = _user_tables()
            keep_tables = user_tables | _system_tables() | {'django_session', 'django_admin_log'}

            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute("ATTACH DATABASE ? AS upload;", (tmp_upload,))
            cur.execute("PRAGMA foreign_keys = OFF;")

            up_tables = [
                row[0] for row in
                cur.execute("SELECT name FROM upload.sqlite_master WHERE type='table';").fetchall()
            ]
            cur_tables = {
                row[0] for row in
                cur.execute("SELECT name FROM main.sqlite_master WHERE type='table';").fetchall()
            }

            imported = 0
            skipped = []
            errors = []
            for tbl in up_tables:
                if tbl in user_tables:
                    skipped.append(f"{tbl} (foydalanuvchi)")
                    continue
                if tbl in _system_tables():
                    skipped.append(f"{tbl} (tizim)")
                    continue
                if tbl.startswith('sqlite_'):
                    continue
                if tbl not in cur_tables:
                    skipped.append(f"{tbl} (joriy bazada yo'q)")
                    continue
                try:
                    cur.execute(f'DELETE FROM main."{tbl}";')
                    cur.execute(f'INSERT INTO main."{tbl}" SELECT * FROM upload."{tbl}";')
                    imported += 1
                except sqlite3.OperationalError as e:
                    errors.append(f"{tbl}: {e}")

            cur.execute("PRAGMA foreign_keys = ON;")
            con.commit()
            cur.execute("DETACH DATABASE upload;")
            con.close()

            messages.success(
                request,
                f"Baza muvaffaqiyatli yuklandi. {imported} ta jadval import qilindi. "
                f"Foydalanuvchilar saqlandi."
            )
            if errors:
                messages.warning(request, "Ba'zi jadvallarda xatolik: " + "; ".join(errors[:3]))
            return HttpResponseRedirect(reverse('admin:index'))

        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            return HttpResponseRedirect(reverse('admin:db_upload'))
        finally:
            try: os.remove(tmp_upload)
            except Exception: pass

    return render(request, 'admin/db_upload.html', {
        'title': "Bazani yuklash (Upload)",
    })


# ===== Clear =====

@staff_member_required
@require_http_methods(["GET", "POST"])
def clear_db(request):
    """Bazani tozalaydi. delete_users=yes bo'lsa, foydalanuvchilar ham o'chiriladi."""
    if request.method == "POST":
        confirm_text = request.POST.get('confirm_text', '').strip()
        delete_users = request.POST.get('delete_users') == 'yes'

        if confirm_text != 'TOZALASH':
            messages.error(request, "Tasdiqlash matni noto'g'ri. 'TOZALASH' deb kiriting.")
            return HttpResponseRedirect(reverse('admin:db_clear'))

        # Backup
        db_path = _db_path()
        if os.path.exists(db_path):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(_backups_dir(), f'db_before_clear_{ts}.sqlite3')
            try:
                shutil.copy2(db_path, backup_path)
            except Exception:
                pass

        user_tables = _user_tables()
        # Tizim jadvallar va foydalanuvchi jadvallari to'liq tozalanmaydi
        keep_tables = set(_system_tables()) | user_tables

        cleared = 0
        users_deleted = 0
        errors = []
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                all_tables = [row[0] for row in cursor.fetchall()]
                cursor.execute("PRAGMA foreign_keys = OFF;")

                # 1) Foydalanuvchi bo'lmagan barcha jadvallarni tozalash
                for tbl in all_tables:
                    if tbl in keep_tables or tbl.startswith('sqlite_'):
                        continue
                    try:
                        cursor.execute(f'DELETE FROM "{tbl}";')
                        cleared += 1
                    except Exception as e:
                        errors.append(f"{tbl}: {e}")

                # 2) delete_users belgilangan bo'lsa — faqat oddiy foydalanuvchilarni o'chirish (adminlar qoladi)
                if delete_users:
                    try:
                        from django.contrib.auth import get_user_model
                        UserModel = get_user_model()
                        utable = UserModel._meta.db_table

                        # Avval o'chiriladigan foydalanuvchilar ID larini olamiz
                        cursor.execute(
                            f'SELECT id FROM "{utable}" WHERE is_staff = 0 AND is_superuser = 0'
                        )
                        del_ids = [row[0] for row in cursor.fetchall()]

                        if del_ids:
                            placeholders = ','.join(['?'] * len(del_ids))
                            # Bog'liq M2M jadvallarni tozalash
                            for m2m in (f'{utable}_groups', f'{utable}_user_permissions'):
                                try:
                                    cursor.execute(
                                        f'DELETE FROM "{m2m}" WHERE user_id IN ({placeholders})',
                                        del_ids
                                    )
                                except sqlite3.OperationalError:
                                    pass
                            # Foydalanuvchilarning o'zlarini o'chirish
                            cursor.execute(
                                f'DELETE FROM "{utable}" WHERE id IN ({placeholders})',
                                del_ids
                            )
                            users_deleted = len(del_ids)
                    except Exception as e:
                        errors.append(f"users: {e}")

                cursor.execute("PRAGMA foreign_keys = ON;")

            msg = f"Baza tozalandi: {cleared} ta jadval."
            if delete_users:
                msg += f" {users_deleted} ta oddiy foydalanuvchi o'chirildi (adminlar saqlandi)."
            else:
                msg += " Foydalanuvchilar saqlandi."
            messages.success(request, msg)

            if errors:
                messages.warning(request, "Ba'zi jadvallarda xatolik: " + "; ".join(errors[:3]))
            return HttpResponseRedirect(reverse('admin:index'))

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {e}")
            return HttpResponseRedirect(reverse('admin:db_clear'))

    return render(request, 'admin/db_clear.html', {
        'title': "Bazani tozalash",
    })
