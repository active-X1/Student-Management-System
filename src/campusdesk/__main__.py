"""Allow ``python -m campusdesk``."""

from campusdesk.launcher import main

if __name__ == "__main__":
    raise SystemExit(main())
