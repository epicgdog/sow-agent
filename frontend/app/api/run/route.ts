import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import { writeFileSync, unlinkSync, mkdtempSync, rmSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

export const maxDuration = 300; // 5 min for agent run

type RunBody = {
  repoUrl: string;
  sowContent: string;
  autoPush?: boolean;
};

export async function POST(request: NextRequest) {
  let tmpDir: string | null = null;
  let sowPath: string | null = null;

  try {
    const body = (await request.json()) as RunBody;
    const { repoUrl, sowContent, autoPush } = body;

    if (!repoUrl?.trim()) {
      return NextResponse.json(
        { error: "repoUrl is required" },
        { status: 400 }
      );
    }

    // Write SOW to a temp file for the runner
    tmpDir = mkdtempSync(join(tmpdir(), "sow-run-"));
    sowPath = join(tmpDir, "sow_reference.md");
    writeFileSync(sowPath, sowContent ?? "", "utf8");

    const projectRoot = join(process.cwd(), "..");
    const sowsystemDir = join(projectRoot, "sowsystem");
    const runnerPy = join(sowsystemDir, "runner.py");

    const args = [
      runnerPy,
      repoUrl.trim(),
      "--sow",
      sowPath,
      "--workspace-dir",
      join(sowsystemDir, "workspaces"),
    ];
    if (autoPush) {
      args.push("--push");
    }

    const env = { ...process.env };
    if (autoPush && process.env.GITHUB_TOKEN) {
      env.GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    }

    const log: string[] = [];
    const exitCode = await new Promise<number>((resolve) => {
      const proc = spawn("python3", args, {
        cwd: sowsystemDir,
        env,
        stdio: ["ignore", "pipe", "pipe"],
      });
      proc.stdout?.setEncoding("utf8");
      proc.stderr?.setEncoding("utf8");
      proc.stdout?.on("data", (chunk) => log.push(String(chunk)));
      proc.stderr?.on("data", (chunk) => log.push(String(chunk)));
      proc.on("close", (code) => resolve(code ?? 1));
    });

    const fullLog = log.join("");
    const passed = exitCode === 0;
    const branchMatch = fullLog.match(/Pushed to branch:\s*(\S+)/);

    return NextResponse.json({
      success: passed,
      log: fullLog,
      branch: branchMatch ? branchMatch[1] : undefined,
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return NextResponse.json(
      { error: "Run failed", detail: message },
      { status: 500 }
    );
  } finally {
    if (sowPath) {
      try {
        unlinkSync(sowPath);
      } catch (_) {}
    }
    if (tmpDir) {
      try {
        rmSync(tmpDir, { recursive: true });
      } catch (_) {}
    }
  }
}
