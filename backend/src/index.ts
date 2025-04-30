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

    // Here you can access the file data
    const buffer = await data.toBuffer();
    const filename = data.filename;
    const mimetype = data.mimetype;

    // TODO: Process the image buffer here
    // For now, just return a success message
    return {
      message: "File received successfully",
      filename,
      mimetype,
      size: buffer.length,
    };
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
