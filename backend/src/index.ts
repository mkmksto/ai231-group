import multipart from "@fastify/multipart";
import fastify from "fastify";

const server = fastify();

// Register multipart plugin
server.register(multipart, {
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
});

server.get("/", async (request, reply) => {
  return "Hello World";
});

server.post("/api/predict", async (request, reply) => {
  try {
    const data = await request.file();
    if (!data) {
      return reply.status(400).send({ error: "No file uploaded" });
    }

    // Convert file to base64
    const buffer = await data.toBuffer();
    const base64Image = buffer.toString("base64");

    // TODO: Send base64Image to ML model
    // here, we either
    const modelResponse = {
      predicted_class: 1, // Replace with actual model prediction
      confidence: 0.95, // Replace with actual confidence score
    };

    return modelResponse;
  } catch (error) {
    console.error("Error processing file:", error);
    return reply.status(500).send({ error: "Error processing file" });
  }
});

server.listen({ port: 8080 }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});
