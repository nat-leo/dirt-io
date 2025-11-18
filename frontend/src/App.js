import React from "react";
import Map from "./Map";

export default function App() {
  return (
    <Map />
  );
}


// export default function App() {
//   const [map, setMap] = useState(null);
//   const [clickedLocation, setClickedLocation] = useState(null);

//   return (
//     <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
//       <GoogleMap
//         mapContainerStyle={containerStyle}
//         center={center}
//         zoom={12}
//         options={options}
//         onLoad={setMap}
//         onClick={(e) =>
//           setClickedLocation({ lat: e.latLng.lat(), lng: e.latLng.lng() })
//         }
//       >
//         {map && (
//           <MapControl map={map} position={window.google.maps.ControlPosition.TOP_RIGHT}>
//             <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
//               {/* Clicked Location Card */}
//               <div
//                 style={{
//                   backgroundColor: "#fff",
//                   border: "2px solid #fff",
//                   borderRadius: "3px",
//                   boxShadow: "0 2px 6px rgba(0,0,0,.3)",
//                   padding: "10px",
//                   width: "200px",
//                   fontFamily: "Arial, sans-serif",
//                   fontSize: "14px",
//                 }}
//               >
//                 {!clickedLocation ? (
//                   <strong>Click on the map to get coordinates</strong>
//                 ) : (
//                   <>
//                     <strong>Clicked Location</strong>
//                     <br />
//                     Latitude: {clickedLocation.lat.toFixed(6)}
//                     <br />
//                     Longitude: {clickedLocation.lng.toFixed(6)}
//                   </>
//                 )}
//               </div>
//             </div>
//           </MapControl>
//         )}
//         {/* PolygonLayer handles clicks and renders polygons */}
//         {map && <PolygonLayer map={map} />}
//       </GoogleMap>
//     </LoadScript>
//   );
// }
