# MapControl Component

Renders HTML elements (cards, buttons, panels) as overlays on a Google Map.

## Usage

```jsx
import { GoogleMap, LoadScript } from "@react-google-maps/api";
import MapControl from "./MapControl";

<LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
  <GoogleMap mapContainerStyle={{ width: "100%", height: "100%" }} center={{ lat: 37.7749, lng: -122.4194 }} zoom={15}>
    <MapControl position={window.google.maps.ControlPosition.TOP_RIGHT}>
      <div>Overlay content here</div>
    </MapControl>
  </GoogleMap>
</LoadScript>
