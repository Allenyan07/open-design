import React from "react";
import {interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {AvatarImage, avatarSrcFor} from "./avatarLibrary";
import type {ChatSpec} from "./types";

const CONTAINER_THEME = {
  none: {screenBg: "transparent", headerBg: "transparent", bubbleLeft: "#FFFFFF", bubbleRight: "#F4F5F7", subtitle: "#7C7C7C"},
  wechat: {screenBg: "#EDEDED", headerBg: "#EDEDED", bubbleLeft: "#FFFFFF", bubbleRight: "#95EC69", subtitle: "#9A9A9A"},
  telegram: {screenBg: "#DDE8F6", headerBg: "#F5F8FC", bubbleLeft: "#FFFFFF", bubbleRight: "#E2F3FF", subtitle: "#7B8EA5"},
  messenger: {screenBg: "#F3F5F8", headerBg: "#FFFFFF", bubbleLeft: "#FFFFFF", bubbleRight: "#0A84FF", subtitle: "#7E8695"},
} as const;

const Bubble = ({
  message,
  participant,
  chatSpec,
  seenBySpeaker,
}: {
  message: ChatSpec["messages"][number];
  participant: ChatSpec["participants"][number];
  chatSpec: ChatSpec;
  seenBySpeaker: boolean;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const theme = CONTAINER_THEME[chatSpec.sceneConfig.container];
  const isRight = message.side === "right";
  if (frame < message.appearAt) {
    return <div style={{display: "none"}} />;
  }
  const local = frame - message.appearAt;
  const scale = spring({frame: local, fps, config: {damping: 14, stiffness: 180, mass: 0.7}, durationInFrames: 18});
  const x = interpolate(local, [0, 12], [isRight ? 26 : -26, 0], {extrapolateRight: "clamp"});
  const opacity = interpolate(local, [0, 8], [0, 1], {extrapolateRight: "clamp"});
  const bubbleBg = isRight ? theme.bubbleRight : theme.bubbleLeft;
  const textColor = chatSpec.sceneConfig.container === "messenger" && isRight ? "#FFFFFF" : "#1F1F1F";
  const showName =
    chatSpec.sceneConfig.nicknameMode === "always" ||
    (chatSpec.sceneConfig.nicknameMode === "first-message-only" && !seenBySpeaker);
  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        marginBottom: 14,
        opacity,
        alignItems: "flex-start",
        flexDirection: isRight ? "row-reverse" : "row",
        justifyContent: chatSpec.sceneConfig.container === "none" ? (isRight ? "flex-end" : "flex-start") : "unset",
      }}
    >
      <AvatarImage src={avatarSrcFor(participant)} />
      <div style={{maxWidth: "72%", display: "flex", flexDirection: "column", alignItems: isRight ? "flex-end" : "flex-start", gap: 6}}>
        {showName ? <div style={{fontSize: 18, color: "#7C8490", fontWeight: 700}}>{message.speaker}</div> : null}
        <div
          style={{
            background: bubbleBg,
            padding: "16px 22px",
            borderRadius: 16,
            fontSize: 30,
            lineHeight: 1.35,
            fontWeight: 500,
            color: textColor,
            boxShadow: message.highlight ? "0 8px 26px rgba(236,135,120,0.18)" : "0 2px 6px rgba(0,0,0,0.05)",
            border: message.highlight ? "2px solid rgba(235,135,120,0.45)" : "1px solid rgba(0,0,0,0.04)",
            transform: `translateX(${x}px) scale(${scale})`,
            transformOrigin: isRight ? "right center" : "left center",
          }}
        >
          {message.text}
        </div>
      </div>
    </div>
  );
};

export const BubbleScene = ({chatSpec}: {chatSpec: ChatSpec}) => {
  const frame = useCurrentFrame();
  const theme = CONTAINER_THEME[chatSpec.sceneConfig.container];
  const headerOpacity = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  const seen = new Set<string>();
  const participantsByName = new Map(chatSpec.participants.map((participant) => [participant.name, participant]));
  const showContainer = chatSpec.sceneConfig.container !== "none";
  const inner = (
    <>
      {showContainer ? (
        <>
          <div
            style={{
              height: 132,
              background: theme.headerBg,
              borderBottom: "1px solid rgba(0,0,0,0.06)",
              display: "flex",
              alignItems: "flex-end",
              padding: "0 22px 14px",
              opacity: headerOpacity,
              flexShrink: 0,
            }}
          >
            <div style={{fontSize: 40, color: "#1F1F1F", fontWeight: 300, width: 32}}>‹</div>
            <div style={{flex: 1, textAlign: "center", fontSize: 28, fontWeight: 700, color: "#1F1F1F"}}>{chatSpec.title}</div>
            <div style={{fontSize: 36, color: "#1F1F1F", letterSpacing: 3, width: 32, textAlign: "right"}}>···</div>
          </div>
          {chatSpec.sceneConfig.showTimestamp ? (
            <div style={{textAlign: "center", marginTop: 18, marginBottom: 20, color: theme.subtitle, fontSize: 22, fontWeight: 500, opacity: headerOpacity}}>
              {chatSpec.timestamp}
            </div>
          ) : null}
        </>
      ) : null}
      <div style={{padding: showContainer ? "0 22px" : "180px 92px", flex: 1, width: "100%"}}>
        {chatSpec.messages.map((message) => {
          const seenBefore = seen.has(message.speaker);
          seen.add(message.speaker);
          const participant = participantsByName.get(message.speaker);
          if (!participant) return null;
          return <Bubble key={message.id} message={message} participant={participant} chatSpec={chatSpec} seenBySpeaker={seenBefore} />;
        })}
      </div>
    </>
  );
  if (!showContainer) {
    return (
      <div
        style={{
          width: 1080,
          height: 1920,
          display: "flex",
          flexDirection: "column",
          background: "transparent",
        }}
      >
        {inner}
      </div>
    );
  }
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: theme.screenBg,
        display: "flex",
        flexDirection: "column",
        fontFamily: `"PingFang SC", "Alibaba PuHuiTi", "Noto Sans SC", sans-serif`,
        overflow: "hidden",
      }}
    >
      {inner}
    </div>
  );
};
