import express from "express";
import { page } from './page'
startServer();

async function startServer() {
  const app = express();
  app.get("*", async (req, res, next) => {
    res.json({ message: "Hello world" });
  });

  const port = process.env.PORT || 4200;
  app.listen(port);
  console.log(`Server running at http://localhost:${port}`);
}
