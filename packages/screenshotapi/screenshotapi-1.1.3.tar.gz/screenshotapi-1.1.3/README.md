# ScreenshotAPI.io Python Client

An API Client for ScreenshotAPI.io (www.screenshotapi.io)

Will perform a screenshot capture using ScreenshotAPI.io and store the resulting screenshot png file locally on disk given the path prefix specified in the `save_path` argument.

## Installation

```shell
pip install screenshotapi
```

## Usage
```python
import screenshotapi

screenshotapi.get_screenshot(
    apikey='get your free apikey at www.screenshotapi.io',
    capture_request = {
          'url': 'http://www.amazon.com',
          'viewport': '1200x800',
          'fullpage': False,
          'webdriver': 'firefox',
          'javascript': True,
          'fresh': False
        },
        save_path = './'
)
```

## Command Line Usage

The installer also provids a command line interface.  You can use it as follows.

```shell
  $ export SCREENSHOTAPI_KEY=your-key-goes-here
  $ screenshotapi --url http://amazon.com \
                  --viewport 1200x800 \
                  --webdriver firefox \
                  --save-path ./
```

Note that you can provide a `SCREENSHOTAPI_KEY` environment variable that can then be used for subsequent calls, or you can use an `--apikey` argument on each call.

API Key
-------

To get a free API key, go to www.screenshotapi.io.

## License

MIT License

Copyright (c) 2018 Competitor Archive, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
