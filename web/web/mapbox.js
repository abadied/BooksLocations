mapboxgl.accessToken = 'pk.eyJ1IjoiYW1pdHVyOTEiLCJhIjoiY2pvbzhkeHN1MGx0ZzNwbHd6cmVkMXFiMyJ9.pXauUkubGnbAUaewUAJ42Q';
const map = new mapboxgl.Map({
container: 'map',
style: 'mapbox://styles/amitur91/cjpl9tkca0qru2sryt2p06f2d',
center: [-90.405077, 24.283965],
zoom: 1.0
});


// Holds visible books features for filtering
var books = [];
var books_filtered;
var popup = new mapboxgl.Popup({});
var last_line = "0";

//vars for filtering
var search_val="";
var years_before = '2018';
var years_after = '1600';
var sunject_list = [];
var years_filter1;
var years_filter2;
var subject_filter;
var search_filter;

var filterEl = document.getElementById('feature-filter');
var listingEl = document.getElementById('feature-listing');

function showPopAndLine(feature_) {
    var popup_html = ' <div class="left-half">' +
        '<img  class="backup_picture" src="https://covers.openlibrary.org/w/id/' + 
        feature_.properties.cover_url +
        '-M.jpg" /></div>' +
        '<div class="right-half">' +
        '<h3>' +
        feature_.properties.title +
        '</h3>' +
        feature_.properties.author +
        '<img  style="float:right;" src="http://covers.openlibrary.org/a/olid/' +
        feature_.properties.author_key + '-S.jpg" />'+
        '<h5>' +
        feature_.properties.release_year +
        '</h5></div>';
    // Highlight corresponding feature on the map
    popup.setLngLat(feature_.geometry.coordinates)
        //.setLngLat(feature.geometry.coordinates)
        .setHTML(popup_html)
        .addTo(map);
        //drawPolygon(feature_.properties.line)
        drawCircles(feature_.properties.line);
        console.log(feature_.properties.author_key);
};

function removePopAndLine() {
    popup.remove();
    map.removeLayer(last_line);
    last_line = "0"
}

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
                showPopAndLine(feature)
            });
            item.addEventListener('mouseleave', function () {
                removePopAndLine()
            });
            listingEl.appendChild(item);
        });
        // Show the filter input
        filterEl.parentNode.style.display = 'block';
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


//show get visible features to list.
function renderListAfterAction(renderToo){
    var features = map.queryRenderedFeatures({layers: ['books-layer']});
    console.log('rendered has found '+features.length)
    if (features) {
        var uniqueFeatures = getUniqueFeatures(features, "title");
        // Populate features for the listing overlay.
        if (renderToo){
            renderListings(uniqueFeatures);
        }

        // Clear the input container
        //filterEl.value = '';

        // Store the current features in as `books` variable to
        // later use for filtering on `keyup`.
        books = uniqueFeatures;
    }
    else {
        books=[];
    }      
}

map.on('load', function () {
    var empty = document.createElement('p');
    empty.textContent = 'Drag the map to populate results';
    listingEl.appendChild(empty);

    map.on('moveend', function () {
        renderListAfterAction(true);
    });
    allFilters();

    map.on('click', function (e) {
        var features = map.queryRenderedFeatures(e.point, {
            layers: ['books-layer']
        });
        var feature = features[0];
        //console.log(feature)
        if (feature!=undefined){
            showPopAndLine(feature);
        map.flyTo({
            center: feature.geometry.coordinates
        });
        }
    });



    //listeners

    filterEl.addEventListener('keyup', function (e) {
        search_val = normalize(e.target.value);
        allFilters();
    });

    document.getElementById('years-after').addEventListener('mouseup', function (e) {
        years_after = e.target.value;
        allFilters();
    });

    document.getElementById('years-before').addEventListener('mouseup', function (e) {
        years_before = e.target.value;
        allFilters();
    });

    //filter by subject
    document.getElementById('checkboxes').addEventListener('input', function (e) {
        allFilters();
    });

});


function filterBySubjects(){
    //TODO
    subject_filter = true;
    //console.log(subjects_checked);
}

function filterByYears() {
    if (years_after < years_before) {
        years_filter1 = [">=", ["get", "release_year"], years_after];
        years_filter2 = ["<=", ["get", "release_year"], years_before];
        // years_filter = ["all",
        //     [">=", ["get", "release_year"], years_after],
        //     ["<=", ["get", "release_year"], years_before]
        // ];

    } else {
        years_filter1 = ["<=", ["get", "release_year"], years_after];
        years_filter2 = [">=", ["get", "release_year"], years_before];
    };
};

function filterBySearch(){

    renderListAfterAction(false);
    
    if (search_val === "") {
        books_filtered = books;
        search_filter = true;
        //renderListings(filtered);
    }
    else {
        //console.log('books: ' +books.length)
        books_filtered = books.filter(function (feature) {
            var name1 = normalize(feature.properties.title);
            var author1 = normalize(feature.properties.author);
            return (name1.indexOf(search_val) > -1 || author1.indexOf(search_val) > -1);
        });
        console.log('books filtered: ' +books_filtered.length)
        if (books_filtered.length > 0) {
            search_filter = ['match', ['get', 'title'], books_filtered.map(function (feature) {
                return feature.properties.title;
            }), true, false];
        }
        else{
            search_filter=false; 
        }  

}
}

function allFilters(){
    map.setFilter('books-layer',null)
    
    renderListAfterAction(false);
    //console.log('books after null filter: ' + books.length);
    //years filter
    filterByYears();

    //subject filter
    filterBySubjects();

    //search filter
    filterBySearch();
    console.log(search_filter);
    map.setFilter('books-layer', ["all", years_filter1,years_filter2,search_filter]); //,subject_filter,search_filter]);
    renderListAfterAction(false);
    renderListings(books_filtered);
    //console.log('books after search filter: ' + books.length);
}

//renderListings([]);

function drawPolygon(line) {

    if (last_line != "0") {
        map.removeLayer(last_line);
    }
    last_line = (Math.floor((Math.random() * 10000) + 1)).toString();;;
    var list1 = JSON.parse(line);

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
            "line-color": "#972e2e",
            "line-width": 3,
            "line-opacity": 0.5
        }
    }, "books-layer");

};

function drawCircles(line){
    if (last_line != "0") {
        map.removeLayer(last_line);
    }
    last_line = (Math.floor((Math.random() * 10000) + 1)).toString();;;
    var list1 = JSON.parse(line);

    const allPoints = list1.map(point => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: point
        }
    }));

    map.addLayer({
        "id": last_line,
        "type": "circle",
        "source": {
            "type": 'geojson',
            "data": {
                "type": 'FeatureCollection',
                "features": allPoints
            }
        },
        "paint": {
        'circle-color': '#e27c06',
      'circle-radius': {'base': 15,
      'stops': [[12, 15], [18, 180]]},
      'circle-pitch-scale': 'map',
      'circle-stroke-width': 0,
      'circle-blur': 0.4,
      'circle-opacity':0.7,
        }
    }, "books-layer");

};

//search locations
map.addControl(new MapboxGeocoder({
    accessToken: mapboxgl.accessToken
}),'top-left');

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl(),'bottom-right');