import { useEffect, useState } from "react";
import { loadAnnotationPolicy } from "../data/loadData";
import type { AnnotationPolicy } from "../data/types";

let cachedPolicy: AnnotationPolicy | null = null;

/** Reset cache — for testing only. */
export function _resetPolicyCache(): void {
  cachedPolicy = null;
}

export function useAnnotationPolicy(): {
  policy: AnnotationPolicy | null;
  loading: boolean;
} {
  const [policy, setPolicy] = useState<AnnotationPolicy | null>(cachedPolicy);
  const [loading, setLoading] = useState(cachedPolicy === null);

  useEffect(() => {
    if (cachedPolicy) return;
    loadAnnotationPolicy()
      .then((p) => {
        cachedPolicy = p;
        setPolicy(p);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return { policy, loading };
}
