import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import LoginPage from "../pages/LoginPage";
import { AuthContext } from "../context/AuthContext";

describe("LoginPage Component", () => {
  it("renders email and password inputs and submit button", () => {
    const mockContext = {
      login: vi.fn(),
      user: null,
      token: null,
      loading: false,
    };

    render(
      <AuthContext.Provider value={mockContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );

    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/name@example.com/i)).toBeInTheDocument();
    expect(document.querySelector('input[type="password"]')).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("submits the form with provided email and password", async () => {
    const mockLogin = vi.fn().mockResolvedValue({ token: "fake-token" });
    const mockContext = {
      login: mockLogin,
      user: null,
      token: null,
      loading: false,
    };

    render(
      <AuthContext.Provider value={mockContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );

    const emailInput = screen.getByPlaceholderText(/name@example.com/i);
    const passwordInput = document.querySelector('input[type="password"]');
    const submitBtn = screen.getByRole("button", { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "SecretPass123" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "SecretPass123");
    });
  });

  it("displays error message when login fails", async () => {
    const mockLogin = vi.fn().mockRejectedValue({
      response: { data: { message: "Invalid email or password" } },
    });
    const mockContext = {
      login: mockLogin,
      user: null,
      token: null,
      loading: false,
    };

    render(
      <AuthContext.Provider value={mockContext}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthContext.Provider>
    );

    fireEvent.change(screen.getByPlaceholderText(/name@example.com/i), {
      target: { value: "wrong@example.com" },
    });
    fireEvent.change(document.querySelector('input[type="password"]'), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });
});
