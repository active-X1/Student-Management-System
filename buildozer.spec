[app]
title = Campus Desk
package.name = campusdesk
package.domain = io.github.activex1

# main.py lives in the repository root; the code is under src/
source.dir = .
source.include_exts = py,png,svg
source.exclude_dirs = tests, docs, legacy, bin, .git, .github, .venv, venv, __pycache__
version = 2.0.0

# sqlite3 is needed because the app stores students in SQLite.
# (tkinter and nicegui are not needed on a phone and are never imported there.)
requirements = python3,kivy,sqlite3

orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/src/campusdesk/assets/icon-512.png

# 64-bit and 32-bit phones
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
