/**
 * Remotion Template: LinkedIn Post Analysis Video
 * Shows: original post → analysis → improved version → CTA
 * Duration: 60 seconds
 */

import React from 'react';
import { Composition, useVideoConfig, AbsoluteFill, Sequence, interpolate, Easing } from 'remotion';

const COLORS = {
  primary: '#0A66C2',    // LinkedIn blue
  success: '#06A94D',    // Green
  warning: '#F5A623',    // Orange
  text: '#000000',
  lightText: '#666666',
  bg: '#FFFFFF',
  lightBg: '#F5F5F5',
};

const FONTS = {
  heading: '"Inter", sans-serif',
  body: '"Inter", sans-serif',
};

/**
 * Main composition
 */
export const LinkedInPostAnalysisVideo = ({
  prospect = {},
  analysis = {},
  script = '',
}) => {
  const { width, height, fps } = useVideoConfig();

  const prospect_name = prospect.author || 'LinkedIn User';
  const prospect_company = prospect.company || 'Company';
  const post_content = prospect.content || 'Your post content here...';

  const strengths = analysis.strengths || [];
  const gaps = analysis.gaps || [];
  const improvements = analysis.improvements || [];

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, fontFamily: FONTS.body }}>
      {/* [0-5s] Opening: Prospect name + topic */}
      <Sequence from={0} durationInFrames={5 * fps}>
        <OpeningFrame
          name={prospect_name}
          company={prospect_company}
          width={width}
          height={height}
        />
      </Sequence>

      {/* [5-15s] Show their actual post */}
      <Sequence from={5 * fps} durationInFrames={10 * fps}>
        <PostDisplayFrame
          content={post_content}
          likes={prospect.likes || '0'}
          comments={prospect.comments || '0'}
          width={width}
          height={height}
        />
      </Sequence>

      {/* [15-25s] Analysis: strengths + gaps */}
      <Sequence from={15 * fps} durationInFrames={10 * fps}>
        <AnalysisFrame
          strengths={strengths}
          gaps={gaps}
          width={width}
          height={height}
        />
      </Sequence>

      {/* [25-40s] Improved version side-by-side */}
      <Sequence from={25 * fps} durationInFrames={15 * fps}>
        <ImprovedVersionFrame
          originalContent={post_content}
          improvements={improvements}
          width={width}
          height={height}
        />
      </Sequence>

      {/* [40-50s] Value proposition */}
      <Sequence from={40 * fps} durationInFrames={10 * fps}>
        <ValuePropositionFrame width={width} height={height} />
      </Sequence>

      {/* [50-60s] CTA + calendar link */}
      <Sequence from={50 * fps} durationInFrames={10 * fps}>
        <CTAFrame
          name={prospect_name}
          width={width}
          height={height}
        />
      </Sequence>
    </AbsoluteFill>
  );
};

/**
 * [0-5s] Opening frame
 */
const OpeningFrame = ({ name, company, width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ color: COLORS.bg, fontSize: 72, margin: 0, fontWeight: 700 }}>Hi {name}</h1>
      <p style={{ color: COLORS.bg, fontSize: 32, margin: '20px 0 0 0', opacity: 0.9 }}>I analyzed your post on {company}</p>
    </AbsoluteFill>
  );
};

/**
 * [5-15s] Display their post
 */
const PostDisplayFrame = ({ content, likes, comments, width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.lightBg, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
      <div style={{
        backgroundColor: COLORS.bg,
        borderRadius: 8,
        padding: 32,
        maxWidth: 600,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}>
        <p style={{ fontSize: 24, lineHeight: 1.6, color: COLORS.text, margin: '0 0 24px 0' }}>{content}</p>
        <div style={{ display: 'flex', gap: 32, fontSize: 14, color: COLORS.lightText }}>
          <span>👍 {likes} likes</span>
          <span>💬 {comments} comments</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * [15-25s] Analysis frame
 */
const AnalysisFrame = ({ strengths, gaps, width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, display: 'flex', flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center', padding: 40 }}>
      {/* Strengths */}
      <div style={{ flex: 1, paddingRight: 20 }}>
        <h2 style={{ color: COLORS.success, fontSize: 28, marginBottom: 16 }}>✓ What's Working</h2>
        {strengths.slice(0, 2).map((s, i) => (
          <p key={i} style={{ fontSize: 18, color: COLORS.text, marginBottom: 12, lineHeight: 1.4 }}>
            • {s}
          </p>
        ))}
      </div>

      {/* Gaps */}
      <div style={{ flex: 1, paddingLeft: 20 }}>
        <h2 style={{ color: COLORS.warning, fontSize: 28, marginBottom: 16 }}>⚠ Room to Improve</h2>
        {gaps.slice(0, 2).map((g, i) => (
          <p key={i} style={{ fontSize: 18, color: COLORS.text, marginBottom: 12, lineHeight: 1.4 }}>
            • {g}
          </p>
        ))}
      </div>
    </AbsoluteFill>
  );
};

/**
 * [25-40s] Improved version
 */
const ImprovedVersionFrame = ({ originalContent, improvements, width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.lightBg, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
      <h2 style={{ fontSize: 36, color: COLORS.primary, marginBottom: 32 }}>Here's the Improved Version</h2>
      <div style={{ display: 'flex', gap: 32, width: '100%', maxWidth: 1000 }}>
        {/* Original */}
        <div style={{ flex: 1, backgroundColor: COLORS.bg, padding: 24, borderRadius: 8, opacity: 0.6 }}>
          <p style={{ fontSize: 12, color: COLORS.lightText, textTransform: 'uppercase', marginBottom: 8 }}>Original</p>
          <p style={{ fontSize: 16, lineHeight: 1.5, color: COLORS.text }}>{originalContent}</p>
        </div>

        {/* Arrow */}
        <div style={{ fontSize: 48, color: COLORS.primary, display: 'flex', alignItems: 'center' }}>→</div>

        {/* Improved */}
        <div style={{ flex: 1, backgroundColor: COLORS.bg, padding: 24, borderRadius: 8, border: `3px solid ${COLORS.success}` }}>
          <p style={{ fontSize: 12, color: COLORS.success, textTransform: 'uppercase', marginBottom: 8 }}>Improved</p>
          <p style={{ fontSize: 16, lineHeight: 1.5, color: COLORS.text, fontWeight: 500 }}>
            {originalContent.slice(0, 50)}... [stronger hook] [social proof] [clear CTA]
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * [40-50s] Value proposition
 */
const ValuePropositionFrame = ({ width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.primary, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
      <h2 style={{ color: COLORS.bg, fontSize: 48, marginBottom: 24, textAlign: 'center' }}>This is what we do</h2>
      <div style={{ fontSize: 24, color: COLORS.bg, textAlign: 'center', lineHeight: 1.8 }}>
        <p>✓ Analyze your content performance</p>
        <p>✓ Identify gaps & opportunities</p>
        <p>✓ Create 3x more engaging posts</p>
        <p style={{ marginTop: 24, opacity: 0.9 }}>We help [Company] creators 3x their engagement</p>
      </div>
    </AbsoluteFill>
  );
};

/**
 * [50-60s] CTA
 */
const CTAFrame = ({ name, width, height }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
      <h2 style={{ fontSize: 44, color: COLORS.primary, marginBottom: 32, textAlign: 'center' }}>Want to see what this looks like for your content?</h2>
      <div style={{
        backgroundColor: COLORS.primary,
        color: COLORS.bg,
        padding: '16px 48px',
        borderRadius: 8,
        fontSize: 24,
        fontWeight: 600,
        marginBottom: 32,
      }}>
        Schedule 15 minutes
      </div>
      <p style={{ fontSize: 18, color: COLORS.lightText, textAlign: 'center' }}>
        No sales pitch. Just a quick conversation about your content strategy.
      </p>
    </AbsoluteFill>
  );
};

export default LinkedInPostAnalysisVideo;
