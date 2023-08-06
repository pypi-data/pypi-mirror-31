screenshotapi
=============

An API Client for ScreenshotAPI.io (www.screenshotapi.io)

Usage
-----

.. code-block:: python

  import screenshotapi

  screenshotapi.get_screenshot(
      apikey='get your free apikey at www.screenshotapi.io',
      capture_request = {
            'url': 'http://www.amazon.com',
            'viewport': '1200x800',
            'fullpage': False,
            'webdriver': 'firefox',
            'javascript': True
          },
          save_path = './'
  )
