'use client';

import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

export const Count = () => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const socket = io('http://localhost:5000', {
      path: '/socket', // match Flask path
      transports: ['websocket'], // optional: skip polling if you want
    });

    socket.on('connect', () => {
      console.log('Connected to socket');
    });

    socket.on('finger_data', (data) => {
      setCount(data.fingerCount);
    });
  }, []);

  return <>{count}</>;
};
