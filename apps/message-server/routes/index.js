import express from "express";

const router = express.Router();

router.get("/", (req, res) => {
  res.render("index.njk", {
    title: process.env.APP_TITLE || "Message Server",
    env: process.env.NODE_ENV,
  });
});

export default router;
