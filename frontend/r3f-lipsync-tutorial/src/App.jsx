
import { Canvas } from "@react-three/fiber";            // Importing Canvas for rendering 3D scenes using react-three-fiber
import { Experience } from "./components/Experience";   // Importing a custom component for the 3D experience
import { useState, useEffect, useRef } from "react";    // Importing React hooks for state management and lifecycle handling
import { FaPaperPlane } from "react-icons/fa";          // Importing a paper plane icon from react-icons


function App() {
  const [text, setText] = useState("");                   // State to store the user input text
  const [audioUrl, setAudioUrl] = useState("");           // State to store the URL of the generated audio
  const [mouthCuesUrl, setMouthCuesUrl] = useState("");   // State to store the URL of the generated mouth cues
  const [isPlaying, setIsPlaying] = useState(false);      // State to track whether audio is currently playing
  const audioRef = useRef(null);                          // Ref to access the audio element directly

  // Function to handle form submission
  // It sends the user input to the server and retrieves the audio and mouth cues
  // It also handles the state of the audio playback
  // If the audio is already playing or the input is empty, it does nothing
  // If the audio is not playing, it sets the isPlaying state to true
  // It sends a POST request to the server with the user input
  // If the request is successful, it updates the audioUrl and mouthCuesUrl states
  // If there is an error, it logs the error and sets isPlaying to false  
  // The function also clears the input text after submission
  // The audio is played automatically when the audioUrl changes
  const handleSubmit = async () => {
    if (isPlaying || text.trim() === "") return; 

    setIsPlaying(true); 
    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer YOUR_TOKEN_HERE", 
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      setAudioUrl(data.audioUrl);
      setMouthCuesUrl(data.mouthCuesUrl);
      setText(""); 
    } catch (error) {
      console.error("Error receiving response.", error);
      setIsPlaying(false); 
    }
  };

  // Effect to handle audio playback
  // It plays the audio when the audioUrl changes 
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      const audio = audioRef.current;
      audio.load();
      audio.play().catch((err) => {
        console.warn("Audio playback failed due to browser restrictions.", err);
      });

      audio.onended = () => {
        setIsPlaying(false);
      };
    }
  }, [audioUrl]);

  

  return (
    <>
      {/* 3D Model*/}
      {/* The Canvas component from react-three-fiber is used to render the 3D scene */}
      <Canvas shadows camera={{ position: [0, 0, 8], fov: 42 }}>
        <color attach="background" args={["#7f0000"]} />
        <Experience audioUrl={audioUrl} mouthCuesUrl={mouthCuesUrl} />
      </Canvas>

      {/* Chat Box at the Bottom of the Page */}
      <div
        style={{
          position: "absolute",
          bottom: 20,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 10,
          display: "flex",
          alignItems: "center",
          width: "80%",
          maxWidth: "600px",
          backgroundColor: "rgba(255,255,255,0.2)",
          padding: "10px 15px",
          borderRadius: "12px",
          backdropFilter: "blur(10px)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.2)",
        }}
      >
        {/* Input field for user to type messages */}
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSubmit();
          }}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "8px",
            border: "none",
            outline: "none",
            fontSize: "16px",
            backgroundColor: "#fff",
            marginRight: "10px",
          }}
          disabled={isPlaying}                                   // Disable input while audio is playing
        />
        <button
          onClick={handleSubmit}
          style={{
            backgroundColor: isPlaying ? "#9e9e9e" : "#c62828",  // Change color when disabled
            color: "white",
            border: "none",
            borderRadius: "8px",
            padding: "10px 14px",
            cursor: isPlaying ? "not-allowed" : "pointer",       // Change cursor when disabled
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: isPlaying ? 0.7 : 1,                        // Add visual feedback for pressed state
          }}
          disabled={isPlaying}                                   // Disable button while audio is playing
        >
          <FaPaperPlane />
        </button>
      </div>

      {/* Autoplay audio */}
      {audioUrl && <audio ref={audioRef} src={audioUrl} autoPlay />}
    </>
  );
}

// Exporting the App component as the default export
// This allows it to be imported and used in other files
export default App;
