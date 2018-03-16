# GIS Utilities

Files, configs, and useful information for working with and actually using Geographic Information Systems (GIS); e.g.: "Custom maps on the Internet".

## Serving Maps to Users

The ability to view maps online is made possible by a complex pile of software that breaks down the complex pile of tasks necessary for turning lists of numbers (e.g.: coordinates and what's _at_ those coordinates) into something visual that you can interact with.

The extremely simplified high-level process of how a map gets to you in a web browser is:

### 1. Find Sources of Geographic Data

This part is very complicated in its own right, but basically boils down to discovering, vetting, and gaining access to public datasets that provide useful information associated with latitude/longitude coordinates.  There are MANY, MANY projects that provide this data; all at varying levels of completeness, scope, quality, and in many formats.  Governments, non-profit organizations, and large international open source communities all work to create and maintain geographic datasets for public use.  This step is primarily about locating high quality data that you are interested in using to build maps out of.

### 2. Find a place to store Geographic Data

As hinted at in the first step, GIS data comes in many formats.  These formats are standardized in one way or another, and one of the most complicated, time consuming, and resource-intensive tasks in working with GIS data is largely to do with converting data sources from their original format into a different format that best suits your needs.

Furthermore, storing GIS data in a way that is easy for GIS-aware systems to access requires special software and databases.  This is because it is not enough to be able to "select" data; the questions you are regularly asking GIS databases are _spatial_ in nature (e.g.: "What is at these coordinates?" or "How can I drive from here to there?").  And to muddy the waters even more, your coordinates are generally referring to a flat (X, Y) plane, but you live on something closely resembling a sphere.  These special databases, services, and the standards that support them describe _how_ to do that math and then do it for you.

#### Some places where you can store GIS data, and then retrieve it later:

- *PostGIS*: self-hosted, a PostgreSQL extention that adds GIS storage capabilities to a SQL server.  This is far and away the most popular option for storing and querying GIS data on your own computers.

- *WMTS*: A _web mapping tile service_ is a website that provides access to _their_ stored GIS content in a standard way.  Many organizations run their own services, and most of them use a handful of common protocols and standards for accessing the data.  One of the most popular options for storing, curating, and sourcing GIS data is the [ArcGIS WMTS](https://enterprise.arcgis.com/en/server/latest/publish-services/linux/wmts-services.htm).

### 3. Serve your own maps

#### Server Software for providing access to self-hosted data

If you opt to run your own servers to serve GIS data you are storing, you have options.

- [*MapServer*](http://mapserver.org): Open source, written in C.  A very popular high-performance server that can do basically anything you need it to with respect to serving GIS data.

- [*Tegola*](http://tegola.io): Open source, written in Golang.  New on the scene, very lean but has a promising architecture.  Specifically used in this project to serve GIS data stored in a PostGIS database in the [Mapbox Vector Tile Format](https://www.mapbox.com/vector-tiles/).

#### Client Software for consuming WMTS/map server data and presenting it to users

The other half of the serving equation is the client side-- actually putting something on a screen for your users to see and play with.  Within the context of web applications, this is almost exclusively the domain of various JavaScript libraries and projects.

- [*Mapbox GL JS*](https://www.mapbox.com/mapbox-gl-js/api/): The preferred library for this project, Mapbox GL JS integrates very cleanly with their open style format, as well as their [map style design Studio](https://www.mapbox.com/mapbox-studio/), and plays nicely with existing web mapping standards.

- [*Leaflet*](http://leafletjs.com): Another very high quality option with different semantics.  Takes more effort to consume Mapbox-styled maps, but provides a much richer ecosystem for consuming a larger array of existing GIS data systems and formats.
