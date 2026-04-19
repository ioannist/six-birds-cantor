import { create } from "zustand";

export type TheoremLayer = "T0" | "T1" | "hybrid";

export interface AppState {
  selectedConfigId: string;
  selectedWitnessId: string;
  selectedShell: string;
  selectedTheoremLayer: TheoremLayer;
  selectedTimeIndex: number;

  setConfigId: (id: string) => void;
  setWitnessId: (id: string) => void;
  setShell: (shell: string) => void;
  setTheoremLayer: (layer: TheoremLayer) => void;
  setTimeIndex: (index: number) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedConfigId: "default",
  selectedWitnessId: "generated.continuous_full_loop_kernel",
  selectedShell: "audited_shell",
  selectedTheoremLayer: "hybrid",
  selectedTimeIndex: 0,

  setConfigId: (id) => set({ selectedConfigId: id }),
  setWitnessId: (id) => set({ selectedWitnessId: id }),
  setShell: (shell) => set({ selectedShell: shell }),
  setTheoremLayer: (layer) => set({ selectedTheoremLayer: layer }),
  setTimeIndex: (index) => set({ selectedTimeIndex: index }),
}));
