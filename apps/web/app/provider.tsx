/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { lazy, Suspense } from "react";
import { useTheme } from "next-themes";
import { SWRConfig } from "swr";
// Plane Imports
import { WEB_SWR_CONFIG } from "@plane/constants";
import { TranslationProvider } from "@plane/i18n";
import { Toast } from "@plane/propel/toast";
// helpers
import { resolveGeneralTheme } from "@plane/utils";
// mobx store provider
import { StoreProvider } from "@/lib/store-context";
// Bivy — feature flag provider (Phase 4 wire-up of Phase 2 Step 2 / ADR 0007)
import { BivyProvider } from "@/core/lib/bivy/context";

// lazy imports
const AppProgressBar = lazy(function AppProgressBar() {
  return import("@/lib/b-progress/AppProgressBar");
});

const StoreWrapper = lazy(function StoreWrapper() {
  return import("@/lib/wrappers/store-wrapper");
});

const InstanceWrapper = lazy(function InstanceWrapper() {
  return import("@/lib/wrappers/instance-wrapper");
});

export interface IAppProvider {
  children: React.ReactNode;
}

export function AppProvider(props: IAppProvider) {
  const { children } = props;
  // themes
  const { resolvedTheme } = useTheme();

  return (
    <StoreProvider>
      <>
        <AppProgressBar />
        <TranslationProvider>
          <Toast theme={resolveGeneralTheme(resolvedTheme)} />
          <StoreWrapper>
            <InstanceWrapper>
              <Suspense>
                <SWRConfig value={WEB_SWR_CONFIG}>
                  <BivyProvider>{children}</BivyProvider>
                </SWRConfig>
              </Suspense>
            </InstanceWrapper>
          </StoreWrapper>
        </TranslationProvider>
      </>
    </StoreProvider>
  );
}
