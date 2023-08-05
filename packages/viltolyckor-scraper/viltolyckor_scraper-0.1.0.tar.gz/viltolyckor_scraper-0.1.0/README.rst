
This is a scraper for statistical data from the (https://www.viltolycka.se/statistik/viltolyckor-for-respektive-viltslag/)[viltolycka.se]  built on top of the `Statscraper package <https://github.com/jplusplus/statscraper>`.

The scraper is limited to the data avialble through https://www.viltolycka.se/statistik/viltolyckor-for-respektive-viltslag/

Install
-------

.. code:: bash

  $ pip install viltolyckor_scraper


Example usage
-------------

.. code:: python

  from viltolyckor import ViltolyckorScraper

  # Init scraper
  scraper = ViltolyckorScraper()

  # List all available datasets
  datasets = scraper.items
  # [<ViltolyckorDataset: viltolyckor per viltslag>]

  # Select a dataset
  dataset = scraper.items["viltolyckor per viltslag"]

  # List all available dimensions
  datasets = verksamhetsform.dimensions
  # [<Dimension: region>, <Dimension: year>, <Dimension: month>, <Dimension: viltslag>]

  # Make a query
  res = dataset.fetch()  # Get latest available data for whole country by default

  # Analyze the results with Pandas
  df = res.pandas

  # Make a more specific query
  # Get data for a given period
  res = dataset.fetch({"period": "2015"})

  # Or from a specific region (all years)
  res = ds.fetch({"region": u"Stockholms län", "year": "*"})


Develop
------

Set up:

.. code:: bash

  $ pip install -r requirements.txt

Run tests:

.. code:: bash

  $ make tests
