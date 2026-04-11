declare module "react" {
  export type SetStateAction<S> = S | ((prevState: S) => S);
  export type Dispatch<A> = (value: A) => void;

  export function useEffect(
    effect: () => void | (() => void),
    deps?: readonly unknown[]
  ): void;

  export function useMemo<T>(
    factory: () => T,
    deps: readonly unknown[]
  ): T;

  export function useState<S>(
    initialState: S
  ): [S, Dispatch<SetStateAction<S>>];
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: unknown;
  }
}
