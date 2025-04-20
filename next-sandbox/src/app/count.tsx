"use client";

import { useFingerSocket } from "./useFingerSocket";

export const Count = () => {
  const { count, password, success } = useFingerSocket();

  return (
    <>
      <div>{count}</div>
      <div>{password}</div>
      <div
        className={`${success === true ? "bg-green-700" : ""} ${
          success === false ? "bg-red-700" : ""
        }`}
      >
        {success !== null ? `${success}` : ""}
      </div>
    </>
  );
};
