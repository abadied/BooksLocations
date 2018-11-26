mapboxgl.accessToken = 'pk.eyJ1IjoiYW1pdHVyOTEiLCJhIjoiY2pvbzhkeHN1MGx0ZzNwbHd6cmVkMXFiMyJ9.pXauUkubGnbAUaewUAJ42Q';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/amitur91/cjoo8efrd2tbi2squnueoz7kv',
    center: [34.841999, 31.847261],
    zoom: 1.0
});

map.on('click', function (e) {
    var features = map.queryRenderedFeatures(e.point, {
        layers: ['books-layer']
   });

    if (!features.length) {
        return;
    }

    var feature = features[0];
    var popup_html = '<h5>title:</h5><h2>' +
        feature.properties.title +
        '</h2><p><h5>author:</h5><h3>x ' +
        feature.properties.author +
        '</h3></p><img src="' +
        feature.properties.cover_url +
        '" />';

    // Holds visible books features for filtering
    var books = [];

    var filterEl = document.getElementById('feature-filter');
    var listingEl = document.getElementById('feature-listing');

    function renderListings(features) {
        // Clear any existing listings
        listingEl.innerHTML = '';
        if (features.length) {
            features.forEach(function (feature) {
                var prop = feature.properties;
                var item = document.createElement('a');
                //item.href = prop.wikipedia;
                //item.target = '_blank';
                item.textContent = prop.title;
                item.addEventListener('mouseover', function () {
                    // Highlight corresponding feature on the map
                    popup.setLngLat(feature.geometry.coordinates)
                        //.setLngLat(feature.geometry.coordinates)
                        .setHTML(popup_html)
                        .setLngLat(feature.geometry.coordinates)
                        .addTo(map);
                        
                    //add(feature);
                });
                item.addEventListener('mouseleave', function () {
                    popup.remove();
                });

                listingEl.appendChild(item);
            });

            // Show the filter input
            filterEl.parentNode.style.display = 'block';
        } else {
            var empty = document.createElement('p');
            empty.textContent = 'Drag the map to populate results';
            listingEl.appendChild(empty);

            // Hide the filter input
            filterEl.parentNode.style.display = 'none';

            // remove features filter
            map.setFilter('books-layer', ['has', 'title']);
        }
    }

    function normalize(string) {
        return string.trim().toLowerCase();
    }

    function getUniqueFeatures(array, comparatorProperty) {
        var existingFeatureKeys = {};
        // Because features come from tiled vector data, feature geometries may be split
        // or duplicated across tile boundaries and, as a result, features may appear
        // multiple times in query results.
        var uniqueFeatures = array.filter(function (el) {
            if (existingFeatureKeys[el.properties[comparatorProperty]]) {
                return false;
            } else {
                existingFeatureKeys[el.properties[comparatorProperty]] = true;
                return true;
            }
        });

        return uniqueFeatures;
    }
    // Create a popup
    var popup = new mapboxgl.Popup({
            offset: [0, -15]
        })
        .setLngLat(feature.geometry.coordinates)
        .setHTML(popup_html)
        .setLngLat(feature.geometry.coordinates)
        .addTo(map);
        drawPolygon(feature.properties.line);
       

        map.on('moveend', function () {
        var features = map.queryRenderedFeatures({
            layers: ['books-layer']
        });


        if (features) {
            var uniqueFeatures = getUniqueFeatures(features, "id");
            // Populate features for the listing overlay.
            renderListings(uniqueFeatures);

            // Clear the input container
            filterEl.value = '';

            // Store the current features in sn `airports` variable to
            // later use for filtering on `keyup`.
            books = uniqueFeatures;
        }
    });


    filterEl.addEventListener('keyup', function (e) {
        var value = normalize(e.target.value);

        // Filter visible features that don't match the input value.
        var filtered = books.filter(function (feature) {
            var name = normalize(feature.properties.title);
            return name.indexOf(value) > -1;
        });

        // Populate the sidebar with filtered results
        renderListings(filtered);

        // Set the filter to populate features into the layer.
        map.setFilter('books', ['match', ['get', 'title'], filtered.map(function (feature) {
            return feature.properties.title;
        }), true, false]);
    });

    // Call this function on initialization
    // passing an empty array to render an empty state
    renderListings([]);
});


var last_line ="0";

function drawPolygon(line) {


 if (last_line!="0"){
     map.removeLayer(last_line);
 }
 last_line =(Math.floor((Math.random() * 10000) + 1)).toString();;;
    var list1 = JSON.parse(line);
    //console.log(list1);

    map.addLayer({
        "id": last_line,
        "type": "line",
        "source": {
            "type": "geojson",
            "data": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": list1
                }
            }
        },
        "layout": {
            "line-join": "round",
            "line-cap": "round"
        },
        "paint": {
            "line-color": "#888",
            "line-width": 8
        }
    });

};


//search locations
map.addControl(new MapboxGeocoder({
    accessToken: mapboxgl.accessToken
}));

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());