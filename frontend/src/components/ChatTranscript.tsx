import type { ChatMessage } from "../types/promise";

function MessageText({ message }: { message: ChatMessage }) {
  if (!message.highlight || !message.text.includes(message.highlight)) {
    return <>{message.text}</>;
  }
  const [before, after] = message.text.split(message.highlight);
  return (
    <>
      {before}
      <mark className="rounded-[3px] bg-[#FFE8A3] px-[2px] py-[1px] text-ink">
        {message.highlight}
      </mark>
      {after}
    </>
  );
}

interface ChatTranscriptProps {
  messages: ChatMessage[];
}

export function ChatTranscript({ messages }: ChatTranscriptProps) {
  return (
    <div className="flex flex-col gap-2">
      {messages.map((message, index) => {
        const isMe = message.speaker === "me";
        return (
          <p
            key={index}
            className={`max-w-[82%] rounded-[14px] px-[13px] py-[10px] text-[13.5px] leading-[1.5] ${
              isMe
                ? "self-end rounded-br-[5px] bg-primary text-white"
                : "self-start rounded-bl-[5px] bg-bg text-ink"
            }`}
          >
            <MessageText message={message} />
          </p>
        );
      })}
    </div>
  );
}
