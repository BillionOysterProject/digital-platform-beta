.PHONY: db gis-server setup-postgis

db:
	docker run \
		--rm \
		--interactive \
		--tty \
		--publish 5432:5432 \
		--volume $(PWD)/db:/var/lib/postgresql/data \
		--env POSTGRES_DB=gis \
		--env POSTGRES_USER=gis \
		--env POSTGRES_PASSWORD=gis \
		mdillon/postgis

setup-postgis:
	# Uses the Imposm project + the Spinnaker script set to import an OpenStreetMap
	# dataset into a running PostGIS server.
	#
	# OpenStreetMap data: http://download.geofabrik.de/north-america.html
	#             Imposm: https://imposm.org
	#   Spinnaker GitHub: https://github.com/colemanm/spinnaker
	#
	imposm \
		-U gis \
		-d gis \
		-m ./spinnaker/osm/spinnaker-mapping.py \
		--read \
		--write \
		--optimize \
		--deploy-production-tables \
		us-northeast-latest.osm.pbf

gis-server:
	which tegola || go get -u -v 'github.com/go-spatial/tegola/cmd/tegola'
	tegola serve
