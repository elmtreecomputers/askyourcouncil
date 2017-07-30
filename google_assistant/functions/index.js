// Copyright 2016, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the 'License');
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

'use strict';

process.env.DEBUG = 'actions-on-google:*';
const ApiAiApp = require('actions-on-google').ApiAiApp;
const functions = require('firebase-functions');
const firebaseAdmin = require('firebase-admin');
var fs = require('fs');
const distance = require('./distance');
firebaseAdmin.initializeApp(functions.config().firebase);
const googleMapsClient = require('@google/maps').createClient({
  key: "<fill your google maps key>"
});

// API.AI actions
const WELCOME_ACTION = 'input.welcome';
const REQUEST_NAME_PERMISSION_ACTION = 'request_name_permission';
const REQUEST_LOC_PERMISSION_ACTION = 'request_location_permission';
const READ_MIND_ACTION = 'read_mind';
const UNHANDLED_DEEP_LINK_ACTION = 'deeplink.unknown';

// Entities/Firebase data keys
const LOCATION_DATA = 'location';
const NAME_DATA = 'name';

function encodeAsFirebaseKey (string) {
  return string.replace(/%/g, '%25')
    .replace(/\./g, '%2E')
    .replace(/#/g, '%23')
    .replace(/\$/g, '%24')
    .replace(/\//g, '%2F')
    .replace(/\[/g, '%5B')
    .replace(/\]/g, '%5D');
}

// [START permissions]
exports.namePsychic = functions.https.onRequest((request, response) => {
  console.log('Request headers: ' + JSON.stringify(request.headers));
  console.log('Request body: ' + JSON.stringify(request.body));

  const app = new ApiAiApp({request, response});

  let hasScreen =
    app.hasSurfaceCapability(app.SurfaceCapabilities.SCREEN_OUTPUT);

  function sayName (displayName) {
    return `<speak>I am reading your mind now. \
      <break time="2s"/> This is easy, you are ${displayName} \
      <break time="500ms"/> I hope I pronounced that right. \
      <break time="500ms"/> Okay! I am off to read more minds.</speak>`;
  }

  function sayLocation (city) {
    return `<speak>here are your nearest child care centers. \
      <break time="2s"/>  ${city} </speak>`;
  }

  function greetUser (app) {
   app.ask(`<speak>Welcome to Ask your council Casey app! <break time="500ms"/> \
       What services would you like to avail today?\
	  I can find facilities near you, find bin date, provide news and events near you, or report a bin collection issue\
	  </speak>`);
  }

  function unhandledDeepLinks (app) {
    app.ask("not applicable");
  }

  function requestNamePermission (app) {
    let permission = app.SupportedPermissions.NAME;
    app.data.permission = permission;
    return requestPermission(app, permission, NAME_DATA, sayName);
  }

  function requestLocationPermission (app) {
    let permission;
    // If the request comes from a phone, we can't use coarse location.
    if (hasScreen) {
      permission = app.SupportedPermissions.DEVICE_PRECISE_LOCATION;
    } else {
      permission = app.SupportedPermissions.DEVICE_COARSE_LOCATION;
    }
    app.data.permission = permission;
    return requestPermission(app, permission, LOCATION_DATA, sayLocation);
  }

  function requestPermission (app, permission, firebaseKey, speechCallback) {
    return new Promise(function (resolve, reject) {
      let userId = app.getUser().user_id;
      firebaseAdmin.database().ref('users/' + encodeAsFirebaseKey(userId))
        .once('value', function (data) {
          if (data && data.val() && data.val()[firebaseKey]) {
            let speechOutput = speechCallback(data.val()[firebaseKey]);
            resolve(app.tell(speechOutput));
          } else {
            resolve(app.askForPermission('To read your mind', permission));
          }
        });
    });
  }

  // Parse city name from the results returned by Google Maps reverse geocoding.
  function parseCityFromReverseGeocoding (results) {
    let addressComponents = results[0].address_components;
    for (let component of addressComponents) {
      for (let type of component.types) {
        if (type === 'locality') {
          return component.long_name;
        }
      }
    }
  }

  function readMind (app) {
    if (app.isPermissionGranted()) {
      let permission = app.data.permission;
      let userData;
      let firebaseKey;
      let speechCallback;
      if (permission === app.SupportedPermissions.NAME) {
        userData = app.getUserName().displayName;
        firebaseKey = NAME_DATA;
        speechCallback = sayName;
        readMindResponse(app, userData, firebaseKey, speechCallback);
      } else if (permission === app.SupportedPermissions.DEVICE_COARSE_LOCATION) {
        userData = app.getDeviceLocation().city;
        firebaseKey = LOCATION_DATA;
        speechCallback = sayLocation;
        readMindResponse(app, userData, firebaseKey, speechCallback);
      } else if (permission === app.SupportedPermissions.DEVICE_PRECISE_LOCATION) {
        // If we required precise location, it means that we're on a phone.
        // Because we will get only latitude and longitude, we need to reverse geocode
        // to get the city.
        let deviceCoordinates = app.getDeviceLocation().coordinates;
        let latLng = [deviceCoordinates.latitude, deviceCoordinates.longitude];
		let latLngKey = {latitude:deviceCoordinates.latitude,longitude: deviceCoordinates.longitude};
		var childDataParsed = JSON.parse(fs.readFileSync('./child.json', 'utf8'));
		let prop_name ;
		let prop_add;
		let co_ordinates;
		var prop_dist;
		var data ;
		var smallestdist = Number.MAX_VALUE;;
		//childDataParsed.features.length
		for (let i = 0; i < childDataParsed.features.length; i++) { //todo fix end
			let feature = childDataParsed.features[i];
			prop_name = feature.properties.name;
			prop_add = feature.properties.address;
			
			co_ordinates = feature.geometry.coordinates;
			var _kCord = {latitude: co_ordinates[1], longitude: co_ordinates[0]};
		
			prop_dist = distance.getDistance(_kCord.latitude, _kCord.longitude,latLngKey.latitude, latLngKey.longitude);
			prop_dist = prop_dist.toFixed(2);
			 if (prop_dist < smallestdist){
				  smallestdist = Math.min(smallestdist, prop_dist);
				  data = prop_name + " is at " +prop_add + " at a distance of " +prop_dist + "kilometers";
			 }
			 
			
		}
		
		//smallestDistance = smallestDistance;
        googleMapsClient.reverseGeocode({latlng: latLng}, function (err, response) {
          if (!err) {
            userData = parseCityFromReverseGeocoding(response.json.results);
            firebaseKey = LOCATION_DATA;
            speechCallback = sayLocation;
            readMindResponse(app, data , firebaseKey, speechCallback);
          } else {
            readMindError();
          }
        });
      } else {
        readMindError();
      }
    } else {
      readMindError();
    }
  }

  function readMindResponse (app, userData, firebaseKey, speechCallback) {
    let userId = app.getUser().user_id;

      // Save [User ID]:[{<name or location>: <data>}] to Firebase
      // Note: Users can reset User ID at any time.
    firebaseAdmin.database().ref('users/' + encodeAsFirebaseKey(userId)).update({
      [firebaseKey]: userData
    });

    app.tell(speechCallback(userData));
  }

  function readMindError () {
      // User did not grant permission or reverse geocoding failed.
    app.tell(`<speak>Wow! <break time="1s"/> This has never \
        happened before. I cannot read your mind. I need more practice. \
        Ask me again later.</speak>`);
  }

  let actionMap = new Map();
  actionMap.set(WELCOME_ACTION, greetUser);
  actionMap.set(UNHANDLED_DEEP_LINK_ACTION, unhandledDeepLinks);
  actionMap.set(REQUEST_NAME_PERMISSION_ACTION, requestNamePermission);
  actionMap.set(REQUEST_LOC_PERMISSION_ACTION, requestLocationPermission);
  actionMap.set(READ_MIND_ACTION, readMind);

  app.handleRequest(actionMap);
});
// [END permissions]
