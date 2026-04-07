import { useEffect, useState } from "react";

import { Badge } from "../../../components/ui/badge";
import { Input } from "../../../components/ui/input";
import { useCustomerSearch } from "../hooks/useCustomerSearch";
import type { CustomerSearchResultType } from "../types/customers.types";

type CustomerSelectorProps = {
  onSelect: (customer: CustomerSearchResultType) => void;
  placeholder?: string;
};

function getCustomerTypeLabel(customerType: CustomerSearchResultType["customer_type"]): string {
  return customerType === "persona_natural" ? "Persona Natural" : "Juridico";
}

export function CustomerSelector({
  onSelect,
  placeholder = "Buscar cliente por nombre o identificacion",
}: CustomerSelectorProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const { results, isLoading } = useCustomerSearch(query);

  useEffect(() => {
    setIsOpen(query.trim().length >= 2);
  }, [query]);

  return (
    <div className="relative w-full space-y-2">
      <Input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder={placeholder}
      />

      {isOpen ? (
        <div className="absolute z-20 w-full rounded-lg border border-slate-300 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900">
          {query.trim().length < 2 ? (
            <p className="px-3 py-2 text-sm text-slate-600 dark:text-slate-300">
              Ingrese al menos 2 caracteres para buscar
            </p>
          ) : isLoading ? (
            <p className="px-3 py-2 text-sm text-slate-600 dark:text-slate-300">Buscando...</p>
          ) : results.length === 0 ? (
            <p className="px-3 py-2 text-sm text-slate-600 dark:text-slate-300">Sin resultados.</p>
          ) : (
            <ul className="max-h-72 overflow-y-auto">
              {results.map((customer) => (
                <li key={customer.id}>
                  <button
                    type="button"
                    className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left hover:bg-slate-100 dark:hover:bg-slate-800"
                    onClick={() => {
                      onSelect(customer);
                      setQuery(`${customer.name} - ${customer.identification_number}`);
                      setIsOpen(false);
                    }}
                  >
                    <span className="text-sm text-slate-900 dark:text-slate-100">
                      {customer.name} - {customer.identification_number}
                    </span>
                    <Badge
                      className={
                        customer.customer_type === "persona_natural"
                          ? "bg-teal-200 text-teal-900 dark:bg-teal-900/60 dark:text-teal-100"
                          : "bg-fuchsia-200 text-fuchsia-900 dark:bg-fuchsia-900/60 dark:text-fuchsia-100"
                      }
                    >
                      {getCustomerTypeLabel(customer.customer_type)}
                    </Badge>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : null}
    </div>
  );
}
