/**
 * Trading Dashboard Route
 * Redirects to main /trading page which contains the full dashboard
 */

import { redirect } from "next/navigation";

export default function TradingDashboardPage() {
  redirect("/trading");
}
