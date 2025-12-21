/**
 * Settings Tab Component
 * Trading preferences and configuration
 */

"use client";

import { useState } from "react";
import type { SessionName } from "@/lib/trading/types";
import { TRADING_PAIRS, DEFAULT_TRADING_SETTINGS } from "@/lib/trading/constants";

export function SettingsTab() {
  const [settings, setSettings] = useState(DEFAULT_TRADING_SETTINGS);

  const updateSetting = <K extends keyof typeof settings>(key: K, value: typeof settings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">Settings</h2>
          <p className="text-white/50 text-sm">Configure your trading preferences</p>
        </div>
        <button className="px-4 py-2 bg-vulcan-accent text-white rounded-lg hover:bg-vulcan-accent/80 transition-colors font-medium">
          Save Changes
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Risk Management */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Management</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Default Risk Per Trade (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={settings.defaultRiskPercent}
                onChange={(e) => updateSetting("defaultRiskPercent", parseFloat(e.target.value) || 1)}
                className="trading-input w-full"
              />
              <p className="text-xs text-white/40 mt-1">Recommended: 1-2% per trade</p>
            </div>

            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Max Daily Trades
              </label>
              <input
                type="number"
                value={settings.maxDailyTrades}
                onChange={(e) => updateSetting("maxDailyTrades", parseInt(e.target.value) || 3)}
                className="trading-input w-full"
              />
            </div>

            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Max Daily Loss (%)
              </label>
              <input
                type="number"
                step="0.5"
                value={settings.maxDailyLoss}
                onChange={(e) => updateSetting("maxDailyLoss", parseFloat(e.target.value) || 3)}
                className="trading-input w-full"
              />
              <p className="text-xs text-white/40 mt-1">Stop trading when daily loss limit is reached</p>
            </div>
          </div>
        </div>

        {/* Preferred Trading */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Trading Preferences</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Preferred Sessions
              </label>
              <div className="flex flex-wrap gap-2">
                {(["asian", "london", "newyork"] as SessionName[]).map((session) => (
                  <button
                    key={session}
                    onClick={() => {
                      const current = settings.preferredSessions;
                      const updated = current.includes(session)
                        ? current.filter((s) => s !== session)
                        : [...current, session];
                      updateSetting("preferredSessions", updated as SessionName[]);
                    }}
                    className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-all ${
                      settings.preferredSessions.includes(session)
                        ? "bg-vulcan-accent text-white"
                        : "bg-white/5 text-white/50 hover:bg-white/10"
                    }`}
                  >
                    {session}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Preferred Pairs
              </label>
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {TRADING_PAIRS.slice(0, 15).map((pair) => (
                  <button
                    key={pair.symbol}
                    onClick={() => {
                      const current = settings.preferredPairs;
                      const updated = current.includes(pair.symbol)
                        ? current.filter((p) => p !== pair.symbol)
                        : [...current, pair.symbol];
                      updateSetting("preferredPairs", updated);
                    }}
                    className={`px-2 py-1 rounded text-xs transition-all ${
                      settings.preferredPairs.includes(pair.symbol)
                        ? "bg-vulcan-accent text-white"
                        : "bg-white/5 text-white/50 hover:bg-white/10"
                    }`}
                  >
                    {pair.symbol}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs text-white/40 uppercase tracking-wider mb-2">
                Timezone
              </label>
              <select
                value={settings.timezone}
                onChange={(e) => updateSetting("timezone", e.target.value)}
                className="trading-input w-full"
              >
                <option value="America/New_York">Eastern Time (EST/EDT)</option>
                <option value="America/Chicago">Central Time (CST/CDT)</option>
                <option value="America/Los_Angeles">Pacific Time (PST/PDT)</option>
                <option value="Europe/London">London (GMT/BST)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Display Options */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Display Options</h3>
          <div className="space-y-4">
            <ToggleSetting
              label="Advanced Mode"
              description="Show additional BTMM indicators and analysis tools"
              checked={settings.showAdvancedMode}
              onChange={(checked) => updateSetting("showAdvancedMode", checked)}
            />

            <ToggleSetting
              label="Auto-Save Screenshots"
              description="Automatically capture entry/exit screenshots"
              checked={settings.autoSaveScreenshots}
              onChange={(checked) => updateSetting("autoSaveScreenshots", checked)}
            />

            <ToggleSetting
              label="Sound Alerts"
              description="Play sounds for trade signals and alerts"
              checked={settings.soundAlerts}
              onChange={(checked) => updateSetting("soundAlerts", checked)}
            />
          </div>
        </div>

        {/* Data Management */}
        <div className="glass rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Data Management</h3>
          <div className="space-y-4">
            <div className="p-4 bg-white/5 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-white">Export Trade History</div>
                  <div className="text-xs text-white/40">Download all trades as CSV</div>
                </div>
                <button className="px-3 py-1.5 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors">
                  Export
                </button>
              </div>
            </div>

            <div className="p-4 bg-white/5 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-white">Import Trades</div>
                  <div className="text-xs text-white/40">Import trades from CSV file</div>
                </div>
                <button className="px-3 py-1.5 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors">
                  Import
                </button>
              </div>
            </div>

            <div className="p-4 bg-trading-bearish/10 border border-trading-bearish/30 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-trading-bearish">Reset All Data</div>
                  <div className="text-xs text-white/40">Clear all trades and settings</div>
                </div>
                <button className="px-3 py-1.5 bg-trading-bearish/20 text-trading-bearish text-sm rounded-lg hover:bg-trading-bearish/30 transition-colors">
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ToggleSetting({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
      <div>
        <div className="text-sm font-medium text-white">{label}</div>
        <div className="text-xs text-white/40">{description}</div>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${
          checked ? "bg-vulcan-accent" : "bg-white/20"
        }`}
      >
        <span
          className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
            checked ? "left-6" : "left-1"
          }`}
        />
      </button>
    </div>
  );
}
