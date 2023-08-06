pixelhosting
============

|pypi|

Python package for PixelHosting - A free image hosting service for Steem projects by @wehmoen.

Installation
-----------------------

The recommended way to install pixelhosting is via ``pip``.

    pip install pixelhosting

Depending on your system, you may need to use ``pip3`` to install packages for Python 3.

Usage
---------------------

.. code:: python

  import os
  from pixelhosting import PixelHosting
  
  def main():
      pixel = PixelHosting(
          os.environ["PIXEL_API_KEY"],
          os.environ["PIXEL_API_KEY_ID"]
      )

      data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

      print(pixel.upload(data))

  if __name__ == '__main__':
      main()


.. |pypi| image:: https://badge.fury.io/py/pixelhosting.svg
  :target: https://pypi.python.org/pypi/pixelhosting/
