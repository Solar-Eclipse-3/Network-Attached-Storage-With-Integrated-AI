import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: "studio-3378748931-552bc.firebaseapp.com",
  projectId: "studio-3378748931-552bc",
  storageBucket: "studio-3378748931-552bc.appspot.com",
  messagingSenderId: "1066148374435",
  appId: "1:1066148374435:web:d1650d7ff79e87a3bddc16",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export { app };
