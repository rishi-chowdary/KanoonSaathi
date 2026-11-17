import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import ClausesTab from "../components/clauses/ClausesTab";
import api from "../services/api";

vi.mock("../services/api", () => {
  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
  };
  return {
    default: mockApi,
    reExplainDocumentClause: vi.fn(),
    simplifyLegalText: vi.fn(),
  };
});

const MOCK_CLAUSES_DATA = {
  data: {
    content: [
      {
        id: "clause-1",
        title: "Early Termination Penalty",
        category: "Termination",
        importance: "HIGH",
        simplifiedSimple: "You must pay 3 months rent if you leave early.",
        simplifiedDetailed: "Detailed explanation of early termination clause.",
        simplifiedProfessional: "Commercial summary of early termination provisions.",
        evidenceQuote: "Tenant shall pay 3 months rent upon early departure.",
        sourcePage: 2,
        quoteVerified: true,
      },
      {
        id: "clause-2",
        title: "Mutual Non-Disclosure",
        category: "Confidentiality",
        importance: "MEDIUM",
        simplifiedSimple: "Neither party will share confidential secrets.",
        simplifiedDetailed: "Detailed confidential treatment of trade secrets.",
        simplifiedProfessional: "Standard mutual non-disclosure obligation.",
        evidenceQuote: "Parties shall keep all proprietary data confidential.",
        sourcePage: 5,
        quoteVerified: true,
      },
    ],
    totalElements: 2,
    totalPages: 1,
    number: 0,
  },
};

describe("ClausesTab Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.get.mockResolvedValue(MOCK_CLAUSES_DATA);
  });

  it("loads and displays clauses list", async () => {
    render(
      <BrowserRouter>
        <ClausesTab documentId="doc-123" />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.get).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText("Early Termination Penalty")).toBeInTheDocument();
      expect(screen.getByText("Mutual Non-Disclosure")).toBeInTheDocument();
    });
  });

  it("filters clauses by category", async () => {
    render(
      <BrowserRouter>
        <ClausesTab documentId="doc-123" />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Early Termination Penalty")).toBeInTheDocument();
    });

    const categorySelect = screen.getAllByRole("combobox")[0];
    fireEvent.change(categorySelect, { target: { value: "Termination" } });

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        "/documents/doc-123/clauses",
        expect.objectContaining({
          params: expect.objectContaining({ category: "Termination" }),
        })
      );
    });
  });

  it("triggers search on form submission", async () => {
    render(
      <BrowserRouter>
        <ClausesTab documentId="doc-123" />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Early Termination Penalty")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search clauses by keyword or title/i);
    fireEvent.change(searchInput, { target: { value: "penalty" } });
    fireEvent.submit(searchInput.closest("form"));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        "/documents/doc-123/clauses",
        expect.objectContaining({
          params: expect.objectContaining({ search: "penalty" }),
        })
      );
    });
  });
});
