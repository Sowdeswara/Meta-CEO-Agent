"""Deprecated launcher for HELM dashboard.

The old interactive dashboard has been removed. To run the application use
Uvicorn directly:

    uvicorn app:app --reload

This script remains only to inform users of the new entrypoint.
"""

import sys


def main():
    print("The HELM dashboard has been deprecated.")
    print("Please start the server using:\n    uvicorn app:app --reload")
    sys.exit(1)


if __name__ == '__main__':
    main()
