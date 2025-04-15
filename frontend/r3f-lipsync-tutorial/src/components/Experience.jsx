import { Environment, OrbitControls, useTexture } from "@react-three/drei";
import { useThree } from "@react-three/fiber";
import { Avatar } from "./Avatar";

export const Experience = ({ audioUrl, mouthCuesUrl }) => {
  const texture = useTexture("textures/signs-symbols-078-infinitychap.com-0588370183.jpg");
  const viewport = useThree((state) => state.viewport);

  return (
    <>
      <OrbitControls />
      <Avatar position={[0, -3, 5]} scale={2} audioUrl={audioUrl} jsonUrl={mouthCuesUrl} />
      <Environment preset="sunset" />
      <mesh>
        <planeGeometry args={[viewport.width, viewport.height]} />
        <meshBasicMaterial map={texture} />
      </mesh>
    </>
  );
};
