import { useEffect, useId, useState } from 'react';

type MermaidModule = typeof import('mermaid');

let mermaidPromise: Promise<MermaidModule> | undefined;

const loadMermaid = () => {
  mermaidPromise ??= import('mermaid').then((module) => {
    const mermaid = module.default;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'neutral',
      htmlLabels: false,
    });
    return module;
  });
  return mermaidPromise;
};

export const MermaidDiagram = ({ chart }: { chart: string }) => {
  const id = useId().replace(/:/g, '');
  const [svg, setSvg] = useState('');
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;

    loadMermaid()
      .then(({ default: mermaid }) => mermaid.render(`diagram-${id}`, chart))
      .then(({ svg: renderedSvg }) => {
        if (active) setSvg(renderedSvg);
      })
      .catch(() => {
        if (active) setFailed(true);
      });

    return () => {
      active = false;
    };
  }, [chart, id]);

  if (failed) {
    return <pre className="overflow-x-auto rounded-lg bg-slate-50 p-4 text-xs">{chart}</pre>;
  }

  return (
    <div
      className="my-5 overflow-x-auto rounded-lg border border-slate-200 bg-white p-4 [&_svg]:mx-auto [&_svg]:h-auto [&_svg]:max-w-full"
      role="img"
      aria-label="Research report diagram"
      dangerouslySetInnerHTML={svg ? { __html: svg } : undefined}
    />
  );
};