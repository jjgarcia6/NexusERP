import { useMemo, useState } from "react";

import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Select } from "../../../components/ui/select";
import { periodPresetSchema, type PeriodPresetType, type PeriodRange } from "../types/reports.types";

type PeriodSelectorProps = {
  value: PeriodRange;
  onChange: (range: PeriodRange) => void;
};

function toIsoRange(from: Date, to: Date): PeriodRange {
  return {
    from: from.toISOString(),
    to: to.toISOString(),
  };
}

function toDateInput(value: string): string {
  return new Date(value).toISOString().slice(0, 10);
}

function buildPresetRange(preset: PeriodPresetType): PeriodRange {
  const now = new Date();
  const end = new Date(now);
  const start = new Date(now);

  switch (preset) {
    case "today":
      start.setUTCHours(0, 0, 0, 0);
      end.setUTCHours(23, 59, 59, 999);
      return toIsoRange(start, end);
    case "last7days":
      start.setUTCDate(start.getUTCDate() - 7);
      start.setUTCHours(0, 0, 0, 0);
      return toIsoRange(start, end);
    case "last30days":
      start.setUTCDate(start.getUTCDate() - 30);
      start.setUTCHours(0, 0, 0, 0);
      return toIsoRange(start, end);
    case "thisMonth":
      start.setUTCDate(1);
      start.setUTCHours(0, 0, 0, 0);
      return toIsoRange(start, end);
    case "custom":
      return toIsoRange(start, end);
  }
}

export function PeriodSelector({ value, onChange }: PeriodSelectorProps) {
  const [preset, setPreset] = useState<PeriodPresetType>("today");
  const [fromDate, setFromDate] = useState<string>(toDateInput(value.from));
  const [toDate, setToDate] = useState<string>(toDateInput(value.to));
  const [error, setError] = useState<string | null>(null);

  const isCustom = preset === "custom";

  const canApplyCustom = useMemo(() => {
    const from = new Date(`${fromDate}T00:00:00.000Z`);
    const to = new Date(`${toDate}T23:59:59.999Z`);
    return from <= to;
  }, [fromDate, toDate]);

  return (
    <div className="space-y-2">
      <div className="flex flex-col gap-2 md:flex-row md:items-center">
        <Select
          value={preset}
          onChange={(event) => {
            const nextPreset = periodPresetSchema.parse(event.target.value);
            setPreset(nextPreset);
            setError(null);

            if (nextPreset !== "custom") {
              onChange(buildPresetRange(nextPreset));
            }
          }}
          className="md:w-52"
        >
          <option value="today">Hoy</option>
          <option value="last7days">Últimos 7 días</option>
          <option value="last30days">Últimos 30 días</option>
          <option value="thisMonth">Este mes</option>
          <option value="custom">Rango personalizado</option>
        </Select>

        {isCustom ? (
          <div className="flex flex-col gap-2 md:flex-row md:items-center">
            <Input
              type="date"
              value={fromDate}
              onChange={(event) => setFromDate(event.target.value)}
            />
            <Input
              type="date"
              value={toDate}
              onChange={(event) => setToDate(event.target.value)}
            />
            <Button
              type="button"
              onClick={() => {
                if (!canApplyCustom) {
                  setError("La fecha de inicio DEBE ser anterior a la fecha de fin");
                  return;
                }

                setError(null);
                onChange({
                  from: new Date(`${fromDate}T00:00:00.000Z`).toISOString(),
                  to: new Date(`${toDate}T23:59:59.999Z`).toISOString(),
                });
              }}
            >
              Aplicar
            </Button>
          </div>
        ) : null}
      </div>

      {error ? <p className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
    </div>
  );
}
