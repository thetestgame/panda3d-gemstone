"""
 * Copyright (C) Rumrunner Games 2020
 * All Rights Reserved
 *
 * Written by Jordan Maxwell <jordan.maxwell@nxt-games.com>, March 7th, 2020
 *
 * RUMRUNNER ENTERTAINMENT CONFIDENTAL
 * _______________________
 *
 * NOTICE:  All information contained herein is, and remains
 * the property of Rumrunner Entertainment and its suppliers,
 * if any.  The intellectual and technical concepts contained
 * herein are proprietary to Rumrunner Entertainment
 * and its suppliers and may be covered by U.S. and Foreign Patents,
 * patents in process, and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material
 * is strictly forbidden unless prior written permission is obtained
 * from Rumrunner Entertainment.
"""

import traceback 
import sys

def run_tests() -> int: 
    """
    Runs the gemstone test's using pytest
    """

    import _pytest
    if not hasattr(_pytest, '__file__'):
        import os
        import _pytest._pluggy
        import py

        _pytest.__file__ = os.getcwd()
        _pytest._pluggy.__file__ = os.getcwd()
        py.__file__ = os.getcwd()

    import pytest
    pytest.main()

    return 0

def main() -> int:
    """
    Main entry point to the Gemstone tests application
    """

    exit_code = 0
    try:
        run_tests()
    except Exception as e:
        print('An error occured while attempting to run test application')
        print('=' * 50)
        print(traceback.format_exc())
        exit_code = 2

    return exit_code

if __name__ == '__main__':
    sys.exit(main())