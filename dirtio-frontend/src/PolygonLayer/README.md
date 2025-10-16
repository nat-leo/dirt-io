# PolygonLayer Component

Renders interactive polygons on a Google Map. Each click adds a polygon around the clicked location.

## Usage

```jsx
import { GoogleMap, LoadScript } from "@react-google-maps/api";
import PolygonLayer from "./PolygonLayer";

<LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
  <GoogleMap mapContainerStyle={{ width: "100%", height: "100%" }} center={{ lat: 37.7749, lng: -122.4194 }} zoom={15}>
    <PolygonLayer />
  </GoogleMap>
</LoadScript>
```

## Future Enhancements

The `PolygonLayer` should connect to our backend to get the correct polygon. This search kinda takes a bit. I can see
a loading animation where the backend yields progressively smaller polygons as it narrows the parcel search until
the exact parcel is found.
