p = "ml_impl/uav_wireless/env.py"
s = open(p).read()
old = '''        r = self.reward_from_terms(self.last_cost)

        self.prev_cov_score = cov_now'''
new = '''        r = self.reward_from_terms(self.last_cost)

        # C3: per-agent counterfactual credit (optional)
        if getattr(c, "credit_mode", "team") == "c3":
            try:
                act = self._active_idx()
                credit = 0.0
                if len(act) > 0 and len(ncov) > 0:
                    for i in act:
                        marg = 0
                        for d in range(c.M):
                            dist = ((self.p[i,0]-self.sensors[d,0])**2 + (self.p[i,1]-self.sensors[d,1])**2)**0.5
                            if dist <= c.R_cov and ncov[d] <= c.K:
                                marg += 1
                        credit += marg / max(c.K * c.M, 1)
                    credit /= len(act)
                if len(adj) > 0:
                    ap = self.articulation_points(adj)
                    conn_credit = float(ap.mean()) if len(ap) else 0.0
                else:
                    conn_credit = 0.0
                r += c.credit_weight * (credit + conn_credit)
            except Exception:
                pass

        self.prev_cov_score = cov_now'''
assert old in s, "old not found"
s = s.replace(old, new)
open(p, "w").write(s)
print("done")
