import sys
import os
import logging

if os.path.join(os.path.dirname(__file__), 'lib') not in sys.path:
  sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
if os.path.join(os.path.dirname(__file__), 'py') not in sys.path:
  sys.path.append(os.path.join(os.path.dirname(__file__), 'py'))
