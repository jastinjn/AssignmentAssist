import { useEffect, useMemo, useRef, useState } from "react";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import type { UIMessage } from "ai";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";

interface StoredMessage {
	role: "user" | "assistant";
	content: string;
	timestamp: string;
}

interface Props {
	historyId: string | null;
	onHistoryCreated: (id: string) => void;
}

export function ChatPanel({ historyId, onHistoryCreated }: Props) {
	const [currentHistoryId, setCurrentHistoryId] = useState(historyId);
	const [initialMessages, setInitialMessages] = useState<UIMessage[]>([]);
	const [loadingHistory, setLoadingHistory] = useState(!!historyId);

	// Stable ref so the custom fetch can call the callback without stale closure
	const onHistoryCreatedRef = useRef(onHistoryCreated);
	onHistoryCreatedRef.current = onHistoryCreated;
	const currentHistoryIdRef = useRef(currentHistoryId);
	currentHistoryIdRef.current = currentHistoryId;

	useEffect(() => {
		if (!historyId) {
			setInitialMessages([]);
			setLoadingHistory(false);
			return;
		}
		setLoadingHistory(true);
		fetch(`/api/chat/histories/${historyId}/messages`)
			.then((r) => r.json())
			.then((msgs: StoredMessage[]) => {
				setInitialMessages(
					msgs.map((m, i) => ({
						id: `history-${i}`,
						role: m.role,
						content: m.content,
						parts: [{ type: "text" as const, text: m.content }],
					})),
				);
			})
			.finally(() => setLoadingHistory(false));
	}, [historyId]);

	// Custom fetch that captures the x-chat-history-id response header
	const customFetch = useMemo(
		() =>
			async (
				input: RequestInfo | URL,
				init?: RequestInit,
			): Promise<Response> => {
				const response = await window.fetch(input, init);
				const newId = response.headers.get("x-chat-history-id");
				if (newId && !currentHistoryIdRef.current) {
					setCurrentHistoryId(newId);
					onHistoryCreatedRef.current(newId);
				}
				return response;
			},
		[], // stable — uses refs for dynamic values
	);

	const transport = useMemo(
		() =>
			new DefaultChatTransport({
				api: "/api/chat/stream",
				body: { historyId: currentHistoryId },
				fetch: customFetch,
			}),
		// Recreate transport when historyId changes (e.g. after first message creates it)
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[currentHistoryId, customFetch],
	);

	const { messages, sendMessage, status, stop } = useChat({
		messages: initialMessages,
		transport,
		onError: (error) => {
			toast.error("Something went wrong", {
				description: error.message || "Failed to get a response. Please try again.",
			});
		},
	});

	const isStreaming = status === "streaming" || status === "submitted";
	const lastMsg = messages[messages.length - 1];
	const assistantHasContent =
		lastMsg?.role === "assistant" &&
		lastMsg.parts?.some((p) => p.type === "text" && (p as { type: "text"; text: string }).text);
	const isThinking = isStreaming && !assistantHasContent;

	function handleSend(text: string) {
		void sendMessage({ text });
	}

	if (loadingHistory) {
		return (
			<div className="flex flex-col flex-1 items-center justify-center text-gray-400 text-sm">
				Loading conversation…
			</div>
		);
	}

	const hasMessages = messages.length > 0 || isStreaming;

	return (
		<div className="flex flex-col flex-1 overflow-hidden">
			{hasMessages ? (
				<div className="flex-1 overflow-y-auto">
					<MessageList messages={messages} isThinking={isThinking} />
				</div>
			) : (
				<div className="flex-1 flex flex-col items-center justify-center gap-4 text-center px-6">
					<p className="text-lg font-medium text-gray-700">Assignment Assist</p>
					<p className="text-sm text-gray-400 max-w-sm">
						Ask me anything about your classes, students, or assignments. I can
						surface insights, identify common mistakes, and track student
						performance.
					</p>
					<div className="flex flex-wrap justify-center gap-2 mt-1">
						{[
							"Which of my students need help?",
							"What are common mistakes?",
							"How is my class performing?",
						].map((suggestion) => (
							<Button
								key={suggestion}
								variant="outline"
								size="sm"
								onClick={() => handleSend(suggestion)}
								className="rounded-full"
							>
								{suggestion}
							</Button>
						))}
					</div>
				</div>
			)}
			<div className="shrink-0">
				<ChatInput
					onSend={handleSend}
					isStreaming={isStreaming}
					onStop={stop}
				/>
			</div>
		</div>
	);
}
