import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AxiosError } from "axios";

import apiClient from "../../../shared/api/client";
import { useHealthCheck } from "./useHealthCheck";

vi.mock("../../../shared/api/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("useHealthCheck", () => {
  it("expone estado operativo cuando backend responde 200 valido", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { status: "ok" } });

    const { result } = renderHook(() => useHealthCheck());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.status).toBe("ok");
    expect(result.current.isError).toBe(false);
  });

  it("expone estado degradado cuando backend responde 503", async () => {
    const error = new AxiosError(
      "Service unavailable",
      "503",
      undefined,
      undefined,
      {
        status: 503,
        statusText: "Service Unavailable",
        headers: {},
        config: { headers: {} as never },
        data: { status: "error", detail: "database unavailable" },
      }
    );

    vi.mocked(apiClient.get).mockRejectedValueOnce(error);

    const { result } = renderHook(() => useHealthCheck());

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.status).toBe("error");
    expect(result.current.isError).toBe(true);
  });
});
