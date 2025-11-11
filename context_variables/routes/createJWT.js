// Minimal, production-friendly example for issuing RS256-signed JWTs
// and (optionally) encrypting a sensitive user payload using IBM's RSA public key.

const fs = require("fs");
const path = require("path");
const express = require("express");
const { v4: uuid } = require("uuid");
const jwtLib = require("jsonwebtoken");
const NodeRSA = require("node-rsa");

const router = express.Router();

/**
 * Load server-side signing private key (PEM).
 * - Keep this file private on your server.
 * - Used to sign JWTs with RS256.
 */
const PRIVATE_KEY_PATH = path.join(__dirname, "../keys/example-jwtRS256.key");
if (!fs.existsSync(PRIVATE_KEY_PATH)) {
  throw new Error(`Private key not found at ${PRIVATE_KEY_PATH}`);
}
const PRIVATE_KEY = fs.readFileSync(PRIVATE_KEY_PATH);

/**
 * Load IBM public key (PEM).
 * - This is used to encrypt the optional user payload so end users cannot read it.
 * - The assistant will decrypt it server-side.
 */
const IBM_PUBLIC_KEY_PATH = path.join(__dirname, "../keys/ibmPublic.key.pub");
if (!fs.existsSync(IBM_PUBLIC_KEY_PATH)) {
  throw new Error(`IBM public key not found at ${IBM_PUBLIC_KEY_PATH}`);
}
const IBM_PUBLIC_KEY = fs.readFileSync(IBM_PUBLIC_KEY_PATH);

/** Cookie lifetime: 45 days (ms) */
const TIME_45_DAYS = 60;

/**
 * Create a signed JWT string for the chat client.
 * - `sub` is the stable user identifier (we keep it constant per browser via cookie).
 * - `user_payload` is optional and will be RSA-encrypted using IBM's public key.
 * - Token expiry is configurable; set a reasonable value for production.
 */
function createJWTString(anonymousUserID, sessionInfo, context) {
  // Base JWT claims. Add/change claims to match your needs.
  const jwtContent = {
    sub: "8763264",
    user_payload: {
      name: "Anonymous",
      custom_message: "Encrypted message",
      custom_user_id: "",
      sso_token: "sso_token",
    },
    context,
  };

  // If your app has an authenticated session, enrich the payload from it.
  if (sessionInfo) {
    jwtContent.user_payload.name = sessionInfo.userName;
    jwtContent.user_payload.custom_user_id = sessionInfo.customUserID;
  }

  // Encrypt user_payload with IBM's RSA public key → base64 string
  // (Assistant will decrypt on its side.)
  if (jwtContent.user_payload) {
    const rsaKey = new NodeRSA(IBM_PUBLIC_KEY);
    const dataString = JSON.stringify(jwtContent.user_payload);
    const utf8Data = Buffer.from(dataString, "utf-8");
    jwtContent.user_payload = rsaKey.encrypt(utf8Data, "base64");
  }

  // Sign the JWT with RS256. Adjust `expiresIn` for your environment.
  // For production, pick a sensible TTL (e.g., "1h", "6h", etc.).
  const jwtString = jwtLib.sign(jwtContent, PRIVATE_KEY, {
    algorithm: "RS256",
    expiresIn: "10000000s", // demo value; replace for production
  });

  return jwtString;
}

/**
 * Retrieve (or set) a stable anonymous ID in a cookie.
 * - This avoids changing user identity mid-session.
 * - If absent, generate one and set a fresh cookie with a 45-day expiration.
 */
function getOrSetAnonymousID(request, response) {
  let anonymousID = request.cookies["ANONYMOUS-USER-ID"];
  if (!anonymousID) {
    anonymousID = `anon-${uuid().slice(0, 5)}`; // short, readable demo ID
  }

  // Refresh cookie expiry each call to keep users “signed” to the same anon ID.
  response.cookie("ANONYMOUS-USER-ID", anonymousID, {
    expires: new Date(Date.now() + TIME_45_DAYS),
    httpOnly: true, // prevent client-side JS from reading it
    sameSite: "Lax",
    secure: false, // set to true if you are on HTTPS in production
  });

  return anonymousID;
}

/**
 * Parse an authenticated session, if your app sets one.
 * - In a real app, you'd verify a session token and fetch user info from a DB/IdP.
 * - Here we expect a JSON string stored in the cookie (for demo simplicity).
 */
function getSessionInfo(request) {
  const sessionInfo = request.cookies?.SESSION_INFO;
  if (!sessionInfo) return null;
  try {
    return JSON.parse(sessionInfo);
  } catch {
    return null;
  }
}

/**
 * Express handler:
 * - Ensures a stable anonymous ID via cookie
 * - Reads any existing session info
 * - Returns a freshly signed JWT as the response body
 */
function createJWT(request, response) {
  const anonymousUserID = getOrSetAnonymousID(request, response);
  const sessionInfo = getSessionInfo(request);
  const context = {
    dev_id: 23424,
    dev_name: "Name",
    is_active: true,
  };
  const token = createJWTString(anonymousUserID, sessionInfo, context);
  response.send(token);
}

// GET / → returns a signed JWT string
router.get("/", createJWT);

module.exports = router;
