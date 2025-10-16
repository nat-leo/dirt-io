import React from "react";
import { GoogleMap, LoadScript } from "@react-google-maps/api";
import PolygonLayer from "./PolygonLayer";

export default {
  title: "Map/PolygonLayer",
  component: PolygonLayer,
};

const containerStyle = { width: "600px", height: "400px" };
const center = { lat: 37.7749, lng: -122.4194 };

export const Default = () => (
  <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
    <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={15}>
      <PolygonLayer />
    </GoogleMap>
  </LoadScript>
);

Default.storyName = "Interactive Polygon Layer";
