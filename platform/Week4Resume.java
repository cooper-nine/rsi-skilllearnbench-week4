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
public class Week4Resume {
    private Process runner;
    private String platformRunId;
    private String runningCampaign;

    @Flow("RSI_WEEK4_LAUNCH")
    public synchronized void launch(String campaignId, String token) throws Exception {
        String workspace = System.getenv("RSI_WEEK4_BENCHMARK_HOME");
        String expected = System.getenv("RSI_WEEK4_TOKEN");
        if (workspace == null || expected == null || expected.length() < 32
                || token == null || campaignId == null
                || !MessageDigest.isEqual(expected.getBytes(StandardCharsets.UTF_8),
                token.getBytes(StandardCharsets.UTF_8))) {
            throw new IllegalArgumentException("Week 4 campaign unavailable");
        }
        String script;
        switch (campaignId) {
            case "week4":
                script = "run_rsi_retests.py";
                break;
            case "week4-earthquake":
                script = "run_earthquake_refinement.py";
                break;
            default:
                throw new IllegalArgumentException("Unknown Week 4 campaign");
        }

        if (runner != null && runner.isAlive()) {
            if (!campaignId.equals(runningCampaign)) {
                throw new IllegalStateException("Another Week 4 campaign is running");
            }
            register("already_running");
            return;
        }

        Path root = Paths.get(workspace).toRealPath();
        Path python = root.resolve(".venv/Scripts/python.exe");
        Path entry = root.resolve("qwen").resolve(script);
        if (!Files.isRegularFile(python) || !Files.isRegularFile(entry)) {
            throw new IllegalStateException("Week 4 runtime is incomplete");
        }

        String runId = UUID.randomUUID().toString();
        Path logs = Files.createDirectories(root.resolve("output/qwen_rsi_flow/platform"));
        ProcessBuilder command = new ProcessBuilder(python.toString(), "-u", entry.toString())
                .directory(root.toFile())
                .redirectErrorStream(true)
                .redirectOutput(logs.resolve(runId + ".log").toFile());
        command.environment().remove("RSI_WEEK4_TOKEN");
        command.environment().put("RSI_WEEK4_PLATFORM_RUN", runId);
        runner = command.start();
        platformRunId = runId;
        runningCampaign = campaignId;
        register("started");
    }

    private void register(String status) {
        FlowEngine.instance().register("launchStatus", status).register("platformRunId", platformRunId);
    }
}
