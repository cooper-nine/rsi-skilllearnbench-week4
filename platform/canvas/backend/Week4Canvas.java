package com.horsecoder.common.whuTalent.core.flow.Run.code;

import cc.eamon.open.flow.core.FlowEngine;
import cc.eamon.open.flow.core.stereotype.Flow;
import cc.eamon.open.flow.spring.FlowComponent;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.UUID;

@FlowComponent
public class Week4Canvas {
    private Process runner;

    @Flow("RSI_WEEK4_CANVAS_LAUNCH")
    public synchronized void launch(String structure, String token) throws Exception {
        String secret = System.getenv("RSI_WEEK4_TOKEN");
        String workspace = System.getenv("RSI_WEEK4_BENCHMARK_HOME");
        if (workspace == null || secret == null || secret.length() < 32 || token == null
                || !MessageDigest.isEqual(secret.getBytes(StandardCharsets.UTF_8),
                   token.getBytes(StandardCharsets.UTF_8))) {
            throw new IllegalArgumentException("Week 4 campaign unavailable");
        }
        if (structure == null || structure.length() > 150000) {
            throw new IllegalArgumentException("Invalid canvas payload");
        }
        if (runner != null && runner.isAlive()) {
            throw new IllegalStateException("A canvas campaign is already running");
        }
        Path root = Paths.get(workspace).toRealPath();
        Path entry = root.resolve("qwen/run_canvas_campaign.py");
        Path python = root.resolve(".venv/Scripts/python.exe");
        if (!Files.isRegularFile(entry) || !Files.isRegularFile(python)) {
            throw new IllegalStateException("Canvas campaign runtime is unavailable");
        }
        String id = UUID.randomUUID().toString();
        Path run = Files.createDirectories(root.resolve("output/qwen_rsi_flow/platform").resolve(id));
        Path canvas = run.resolve("canvas.json");
        Files.write(canvas, structure.getBytes(StandardCharsets.UTF_8));
        ProcessBuilder command = new ProcessBuilder(python.toString(), "-u", entry.toString(), run.toString())
            .directory(root.toFile()).redirectErrorStream(true).redirectOutput(run.resolve("runner.log").toFile());
        command.environment().remove("RSI_WEEK4_TOKEN");
        runner = command.start();
        FlowEngine.instance().register("launchStatus", "started").register("platformRunId", id);
    }
}
