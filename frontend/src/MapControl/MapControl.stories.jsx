import React from "react";
import { GoogleMap, LoadScript } from "@react-google-maps/api";
import MapControl from "./MapControl";

export default {
  title: "Map/MapControl",
  component: MapControl,
};

const containerStyle = { width: "600px", height: "400px" };
const center = { lat: 37.7749, lng: -122.4194 };

export const Default = () => (
  <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
    <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={15}>
      <MapControl position={window.google.maps.ControlPosition.TOP_RIGHT}>
        <div
          style={{
            backgroundColor: "#fff",
            padding: "8px 12px",
            borderRadius: "4px",
            boxShadow: "0 2px 6px rgba(0,0,0,.3)",
            fontFamily: "Arial, sans-serif",
          }}
        >
          Hello World Overlay
        </div>
      </MapControl>
    </GoogleMap>
  </LoadScript>
);

Default.storyName = "Overlay Card + Button";
