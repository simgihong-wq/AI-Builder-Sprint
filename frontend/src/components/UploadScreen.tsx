import { useRef, useState, type DragEvent } from "react";
import { Logo } from "./ui/Logo";
import { Button } from "./ui/Button";
import { BottomBar } from "./ui/BottomBar";
import { LoadingScreen } from "./LoadingScreen";
import { analyzeImages, analyzeText } from "../api/analyze";
import { USE_MOCK } from "../api/config";
import { ApiError, type AnalyzedData } from "../api/types";
import { mockAnalyzedData } from "../data/mockResult";

interface UploadedFile {
  id: string;
  name: string;
  sizeLabel: string;
  pattern: 0 | 1;
  file: File;
}

function formatSize(bytes: number) {
  const mb = bytes / (1024 * 1024);
  if (mb >= 0.1) return `${mb.toFixed(1)}MB`;
  return `${Math.max(1, Math.round(bytes / 1024))}KB`;
}

function FileThumbnail({ pattern }: { pattern: 0 | 1 }) {
  const barsA = [
    { color: "#D5DBE1", align: "left" as const },
    { color: "#BBD5F7", align: "right" as const },
    { color: "#D5DBE1", align: "left" as const },
    { color: "#BBD5F7", align: "right" as const },
  ];
  const barsB = [
    { color: "#BBD5F7", align: "right" as const },
    { color: "#D5DBE1", align: "left" as const },
    { color: "#BBD5F7", align: "right" as const },
    { color: "#D5DBE1", align: "left" as const },
  ];
  const bars = pattern === 0 ? barsA : barsB;
  return (
    <div className="flex h-12 w-[38px] flex-none flex-col gap-[3px] rounded-[7px] bg-bg p-1">
      {bars.map((bar, i) => (
        <i
          key={i}
          className="block h-[5px] rounded-sm"
          style={{
            background: bar.color,
            width: bar.align === "left" ? "70%" : "60%",
            marginLeft: bar.align === "right" ? "auto" : undefined,
          }}
        />
      ))}
    </div>
  );
}

interface UploadScreenProps {
  onAnalyzed: (data: AnalyzedData) => void;
}

export function UploadScreen({ onAnalyzed }: UploadScreenProps) {
  const [tab, setTab] = useState<"cap" | "txt">("cap");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [text, setText] = useState("");
  const [tipOpen, setTipOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [phase, setPhase] = useState<"idle" | "loading" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return;
    const next = Array.from(incoming).map((file, i) => ({
      id: `${file.name}-${Date.now()}-${i}`,
      name: file.name,
      sizeLabel: formatSize(file.size),
      pattern: (files.length + i) % 2 === 0 ? (0 as const) : (1 as const),
      file,
    }));
    setFiles((prev) => [...prev, ...next]);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const canSubmit = tab === "cap" ? files.length > 0 : text.trim().length >= 10;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setErrorMessage(null);
    setPhase("loading");
    try {
      let data: AnalyzedData;
      if (USE_MOCK) {
        await new Promise((resolve) => setTimeout(resolve, 1200));
        data = mockAnalyzedData;
      } else if (tab === "cap") {
        data = await analyzeImages(files.map((f) => f.file));
      } else {
        data = await analyzeText(text.trim());
      }
      onAnalyzed(data);
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.message
          : "분석 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.";
      setErrorMessage(message);
      setPhase("error");
    }
  };

  if (phase === "loading") {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-bg">
      <div className="screen-shell mx-auto flex min-h-screen w-full max-w-[420px] flex-col">
        <div className="flex h-[52px] flex-none items-center px-3">
          <Logo />
        </div>

        <div className="flex-1 px-5 pb-[120px] pt-1">
          <h1 className="mb-2 text-2xl font-bold leading-[1.38] tracking-[-0.03em] text-ink">
            거래 대화를
            <br />
            올려주세요
          </h1>
          <p className="mb-6 text-[15px] leading-[1.5] text-text-secondary">
            빠진 약속이 없는지 확인해드릴게요.
          </p>

          <div className="mb-[18px] flex gap-1.5 rounded-xl bg-[#E9ECEF] p-1">
            <button
              type="button"
              onClick={() => setTab("cap")}
              className={`h-[38px] flex-1 rounded-[9px] text-sm font-semibold tracking-[-0.02em] transition-colors ${
                tab === "cap"
                  ? "bg-surface text-ink shadow-[0_1px_3px_rgba(25,31,40,.1)]"
                  : "bg-transparent text-text-tertiary"
              }`}
            >
              캡처 올리기
            </button>
            <button
              type="button"
              onClick={() => setTab("txt")}
              className={`h-[38px] flex-1 rounded-[9px] text-sm font-semibold tracking-[-0.02em] transition-colors ${
                tab === "txt"
                  ? "bg-surface text-ink shadow-[0_1px_3px_rgba(25,31,40,.1)]"
                  : "bg-transparent text-text-tertiary"
              }`}
            >
              텍스트 붙여넣기
            </button>
          </div>

          {tab === "cap" && (
            <div>
              <div
                onClick={() => inputRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`relative cursor-pointer rounded-[18px] border-[1.5px] border-dashed px-5 py-[34px] text-center transition-colors ${
                  isDragging
                    ? "border-primary bg-[#FAFCFF]"
                    : "border-[#C6D3E2] bg-surface"
                }`}
              >
                <div className="mx-auto mb-3.5 grid h-[54px] w-[54px] place-items-center rounded-2xl bg-primary-soft text-2xl">
                  🖼️
                </div>
                <div className="mb-[5px] flex items-center justify-center gap-1.5">
                  <span className="text-[15.5px] font-bold text-ink">
                    캡처를 여기에 놓거나 탭하세요
                  </span>
                  <button
                    type="button"
                    aria-label="안내 보기"
                    onClick={(e) => {
                      e.stopPropagation();
                      setTipOpen((v) => !v);
                    }}
                    className={`grid h-[19px] w-[19px] flex-none place-items-center rounded-full text-[12px] font-extrabold transition-colors ${
                      tipOpen
                        ? "bg-primary text-white opacity-100"
                        : "bg-border text-text-tertiary opacity-55"
                    }`}
                  >
                    !
                  </button>
                </div>
                <div className="text-[13px] leading-[1.5] text-text-tertiary">
                  여러 장을 한 번에 올릴 수 있어요
                </div>
                <div
                  className="overflow-hidden text-left transition-all duration-300"
                  style={{
                    maxHeight: tipOpen ? 180 : 0,
                    opacity: tipOpen ? 1 : 0,
                    marginTop: tipOpen ? 14 : 0,
                  }}
                >
                  <div className="flex items-start gap-2 rounded-[14px] bg-bg px-[15px] py-[13px]">
                    <span className="text-[13px] leading-[1.6]">🔒</span>
                    <span className="text-[12.5px] font-medium leading-[1.6] text-text-tertiary">
                      원본은 저장하지 않아요. 계좌번호·전화번호는 분석 전에
                      자동으로 가려집니다.
                    </span>
                  </div>
                </div>
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onClick={(e) => e.stopPropagation()}
                  onChange={(e) => addFiles(e.target.files)}
                />
              </div>

              {files.length > 0 && (
                <div className="mt-3 flex flex-col gap-2">
                  {files.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-center gap-[11px] rounded-[14px] bg-surface p-2.5"
                    >
                      <FileThumbnail pattern={file.pattern} />
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-[13.5px] font-semibold text-ink">
                          {file.name}
                        </div>
                        <div className="mt-0.5 text-xs text-text-tertiary">
                          {file.sizeLabel}
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(file.id)}
                        className="grid h-[26px] w-[26px] flex-none place-items-center rounded-full bg-bg text-[13px] text-text-tertiary hover:bg-border hover:text-ink"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-3 rounded-[14px] bg-warning-bg-soft px-4 py-3.5 text-[13px] font-medium leading-[1.6] text-warning-text">
                💡 가격·장소·시간이 오간 부분을 모두 올려주세요. 일부만 올리면
                정해진 약속을 놓칠 수 있어요.
              </div>
            </div>
          )}

          {tab === "txt" && (
            <div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="대화 내용을 그대로 붙여넣으세요."
                className="min-h-[190px] w-full resize-none rounded-[18px] border-0 bg-surface p-[18px] text-[14.5px] leading-[1.7] tracking-[-0.02em] text-ink placeholder:text-text-tertiary focus:outline-none"
              />
              <div className="mt-3 rounded-[14px] bg-warning-bg-soft px-4 py-3.5 text-[13px] font-medium leading-[1.6] text-warning-text">
                💡 캡처가 잘 안 읽힐 때 쓰면 좋아요.
              </div>
            </div>
          )}

          {phase === "error" && errorMessage && (
            <div className="mt-3 rounded-[14px] bg-danger-bg px-4 py-3.5 text-[13px] leading-[1.55] text-danger">
              <p>{errorMessage}</p>
              <button
                type="button"
                onClick={() => onAnalyzed(mockAnalyzedData)}
                className="mt-2 text-xs font-semibold underline underline-offset-2"
              >
                mock 데이터로 보기
              </button>
            </div>
          )}
        </div>

        <BottomBar>
          <Button onClick={handleSubmit} disabled={!canSubmit}>
            {phase === "error" ? "다시 시도" : "분석 시작하기"}
          </Button>
        </BottomBar>
      </div>
    </div>
  );
}
