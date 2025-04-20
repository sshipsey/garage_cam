import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

type FingerData = { fingerCount: number };

export const useFingerSocket = (
  passwordLength = 4,
  passwordAnswer = "5678"
) => {
  const [count, setCount] = useState(0);
  const [password, setPassword] = useState("");
  const [success, setSuccess] = useState<boolean | null>(null);

  const lastCountRef = useRef(0); // 🔐 this avoids causing re-renders

  useEffect(() => {
    const socket: Socket = io("http://localhost:5001", {
      path: "/socket",
      transports: ["websocket"],
    });

    socket.on("connect", () => {
      console.log("Connected to socket");
    });

    socket.on("finger_data", (data: FingerData) => {
      const fingerCount = data.fingerCount;
      setCount(fingerCount);

      if (fingerCount === 0 || fingerCount === lastCountRef.current) {
        setPassword("");
        return;
      }

      setPassword((prev) => {
        const newPass = `${prev}${fingerCount}`;
        lastCountRef.current = fingerCount;

        if (newPass.length === passwordLength) {
          setSuccess(newPass === passwordAnswer);
          return "";
        }

        return newPass;
      });
    });

    return () => {
      socket.disconnect();
    };
  }, [passwordLength, passwordAnswer]); // ✅ stable deps only

  return { count, password, success };
};
