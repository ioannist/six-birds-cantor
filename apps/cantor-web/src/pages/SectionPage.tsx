import { useAppStore } from "../app/store";

interface SectionPageProps {
  title: string;
  description: string;
}

export default function SectionPage({ title, description }: SectionPageProps) {
  const store = useAppStore();

  return (
    <section>
      <h1>{title}</h1>
      <p className="page-subtitle">
        Layer: <code>{store.selectedTheoremLayer}</code> | Witness:{" "}
        <code>{store.selectedWitnessId}</code> | Shell:{" "}
        <code>{store.selectedShell}</code> | Time:{" "}
        <code>{store.selectedTimeIndex}</code>
      </p>
      <p className="page-description">{description}</p>
    </section>
  );
}
